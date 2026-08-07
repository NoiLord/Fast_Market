import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_dotenv() -> None:
    """Мини-загрузчик .env без внешних зависимостей."""
    path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "").split(",") if x.strip().isdigit()]
PAYMENT_DETAILS = os.environ.get("PAYMENT_DETAILS", "Напишите в поддержку для оплаты.")
SUPPORT_USERNAME = os.environ.get("SUPPORT_USERNAME", "")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "Fast_Market_Games_BOT")

if not BOT_TOKEN:
    raise RuntimeError("Укажите BOT_TOKEN в файле .env")