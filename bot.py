import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Token của bot Telegram (Thay thế bằng mã token thực tế)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ID chat của sếp Thanh Luân
CHAT_ID = os.getenv('CHAT_ID')

def send_message(message):
    """
    Gửi tin nhắn đến sếp Thanh Luân qua Telegram.
    
    :param message: Nội dung tin nhắn cần gửi
    """
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Tin nhắn đã được gửi thành công.")
    else:
        print(f"Lỗi khi gửi tin nhắn: {response.text}")

if __name__ == '__main__':
    message = "Chào sếp Thanh Luân!"
    send_message(message)
