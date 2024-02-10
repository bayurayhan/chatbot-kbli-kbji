from pyngrok import ngrok
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PORT = os.environ.get("SERVER_PORT")
API_KEY = os.environ.get("TELEGRAM_API_KEY")
http_tunnel = ngrok.connect(f"http://localhost:{PORT}")

print(http_tunnel.public_url)

url_webhook = f"https://api.telegram.org/bot{API_KEY}/setWebhook?url={http_tunnel.public_url}/api/webhook"
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


ngrok_process = ngrok.get_ngrok_process()

try:
    # Block until CTRL-C or some other terminating event
    ngrok_process.proc.wait()
except KeyboardInterrupt:
    print(" Shutting down server.")

    ngrok.kill()
