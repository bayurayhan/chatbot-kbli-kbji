import requests
import os
import sys
from dotenv import load_dotenv, find_dotenv
from pyngrok import ngrok

load_dotenv(override=True)

API_KEY = os.environ.get("TELEGRAM_API_KEY")
PORT = os.environ.get("SERVER_PORT")
SERVER_DOMAIN = os.environ.get("SERVER_DOMAIN")

print(API_KEY)

def register_webhook(is_server):
    if is_server:
        url = f"https://api.telegram.org/bot{API_KEY}/setWebhook?url=https://{SERVER_DOMAIN}/api/webhook"
    else:
        http_tunnel = ngrok.connect(f"http://localhost:{PORT}")
        print(http_tunnel.public_url)
        url = f"https://api.telegram.org/bot{API_KEY}/setWebhook?url={http_tunnel.public_url}/api/webhook"

    res = requests.get(url)

    if res.status_code == 200:
        print(res.text)
    else:
        raise RuntimeError(res.status_code)

    webhook_info = f"https://api.telegram.org/bot{API_KEY}/getWebhookInfo"
    res = requests.get(webhook_info)

    if res.status_code == 200:
        print(res.text)
    else:
        raise RuntimeError(res.status_code)

    if not is_server:
        ngrok_process = ngrok.get_ngrok_process()
        try:
            ngrok_process.proc.wait()
        except KeyboardInterrupt:
            print("Shutting down server.")
            ngrok.kill()

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["server", "local"]:
        print("Usage: python combined_script.py [server|local]")
        sys.exit(1)

    register_webhook(sys.argv[1] == "server")
