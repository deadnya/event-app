from bot.config import BOT_TOKEN
from bot.telegram_bot import TelegramBot
from bot.utils.logger import logger

def main():
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
        return
    
    logger.info("Initializing Telegram Bot...")
    bot = TelegramBot()
    bot.run()


if __name__ == '__main__':
    main()
