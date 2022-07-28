from decouple import config
from dotenv import load_dotenv

load_dotenv()


try:
    BOT_TOKEN = config("BOT_TOKEN")
    OWNER = config("OWNER")
    STORAGE_CHANNEL = config("STORAGE", cast=int)
    MAIN_CHANNEL = config("MAIN_CHANNEL", cast=int)
except Exception as ex:
    print(ex)
    exit(0)
