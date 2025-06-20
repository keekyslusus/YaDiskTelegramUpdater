import yadisk
import telegram
from telegram.constants import ParseMode
import asyncio
import logging
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

YANDEX_FOLDER_PATHS_STR = os.environ.get('YANDEX_FOLDER_PATHS', '/')
LIST_OF_FOLDERS = [path.strip() for path in YANDEX_FOLDER_PATHS_STR.split(',')]

CHECK_INTERVAL_SECONDS = int(os.environ.get('CHECK_INTERVAL_SECONDS', 120))

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
YANDEX_TOKEN = os.environ['YANDEX_TOKEN']


def get_current_files(y: yadisk.YaDisk, folder_path: str) -> set | None:
    try:
        items = y.listdir(folder_path, limit=1000)
        return {item.name for item in items}
    except yadisk.exceptions.PathNotFoundError:
        logger.error(f"The folder '{folder_path}' was not found. Please check your YANDEX_FOLDER_PATHS environment variable.")
        return None
    except Exception as e:
        logger.error(f"An error occurred fetching files from '{folder_path}': {e}")
        return None


async def main():
    try:
        bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
        y = yadisk.YaDisk(token=YANDEX_TOKEN)
        logger.info("Successfully initialized Telegram Bot and Yandex.Disk clients.")
        if not y.check_token():
            logger.critical("The Yandex.Disk token is invalid or expired. Please get a new one.")
            return
    except Exception as e:
        logger.critical(f"Failed to initialize clients. Error: {e}")
        return

    seen_files_map = {}
    logger.info(f"Performing initial scan for folders: {', '.join(LIST_OF_FOLDERS)}")

    for folder in LIST_OF_FOLDERS:
        initial_files = get_current_files(y, folder)
        if initial_files is not None:
            seen_files_map[folder] = initial_files
            logger.info(f"-> Found {len(initial_files)} existing files in '{folder}'.")

    logger.info("Initial scan complete. Monitoring for new files...")

    while True:
        try:
            logger.debug("Checking for new files across all monitored folders...")

            for folder_path in LIST_OF_FOLDERS:
                if folder_path not in seen_files_map:
                    initial_files = get_current_files(y, folder_path)
                    if initial_files is not None:
                        seen_files_map[folder_path] = initial_files
                        logger.info(f"Successfully initialized previously missing folder '{folder_path}'.")
                    else:
                        continue

                seen_for_this_folder = seen_files_map.get(folder_path, set())
                current_files = get_current_files(y, folder_path)

                if current_files is None:
                    continue

                new_files = current_files - seen_for_this_folder

                if new_files:
                    logger.info(f"Found {len(new_files)} new file(s) in '{folder_path}': {', '.join(new_files)}")
                    for filename in new_files:
                        message = (
                            f"🔔 <b>New file added to Yandex.Disk!</b>\n\n"
                            f"📄 <b>File:</b> <code>{filename}</code>\n"
                            f"📂 <b>Folder:</b> <code>{folder_path}</code>"
                        )
                        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.HTML)
                        seen_files_map[folder_path].add(filename)

            logger.debug(f"Check cycle complete. Waiting for {CHECK_INTERVAL_SECONDS} seconds.")
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)

        except Exception as e:
            logger.error(f"An unexpected error occurred in the main loop: {e}")
            logger.info("Waiting for a longer period (300s) before retrying...")
            await asyncio.sleep(300)


if __name__ == '__main__':
    asyncio.run(main())