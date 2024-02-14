import requests
import os
import requests
from dotenv import load_dotenv
load_dotenv()

PORT = os.environ.get("SERVER_PORT")
API_KEY = os.environ.get("TELEGRAM_API_KEY")

url_webhook = f"https://api.telegram.org/bot{API_KEY}/setWebhook?url=https://{os.environ.get("SERVER_DOMAIN", "")}/api/webhook"
res = requests.get(url_webhook)
# Check the status code
if res.status_code == 200:
    # Print the response content
    print(res.text)
else:
    raise RuntimeError(res.status_code)

webhook_info = f"https://api.telegram.org/bot{API_KEY}/getWebhookInfo"

res = requests.get(webhook_info)

# Check the status code
if res.status_code == 200:
    # Print the response content
    print(res.text)
else:
    raise RuntimeError(res.status_code)
