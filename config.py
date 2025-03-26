from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
BRANCH_ADMINS = {
    "branch_1": int(os.getenv("BRANCH_1_ADMIN", 0)),
    "branch_2": int(os.getenv("BRANCH_2_ADMIN", 0)),
    "branch_3": int(os.getenv("BRANCH_3_ADMIN", 0)),
    "branch_4": int(os.getenv("BRANCH_4_ADMIN", 0)),
    "branch_5": int(os.getenv("BRANCH_5_ADMIN", 0)),
    "branch_6": int(os.getenv("BRANCH_6_ADMIN", 0))
}