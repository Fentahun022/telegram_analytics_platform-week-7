import os
import json
import asyncio
from telethon import TelegramClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_NAME = 'telegram_scraper'

CHANNELS = [
    'lobelia4cosmetics',
    'tikvahpharma',
    'chemed_ethiopia'
    # Add more channels from https://et.tgstat.com/medicine
]

DATA_LAKE_MESSAGES_PATH = 'data/raw/telegram_messages'
DATA_LAKE_IMAGES_PATH = 'data/raw/telegram_images'

async def scrape_channel(client, channel_name):
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = os.path.join(DATA_LAKE_MESSAGES_PATH, today)
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"{channel_name}.json")
    messages_data = []

    print(f"Scraping channel: {channel_name}")
    async for message in client.iter_messages(channel_name, limit=200): # Adjust limit as needed
        if message.text or message.photo:
            message_dict = message.to_dict()
            messages_data.append(message_dict)

            # Download image if it exists
            if message.photo:
                image_path = os.path.join(DATA_LAKE_IMAGES_PATH, f"{message.id}.jpg")
                if not os.path.exists(image_path):
                    print(f"Downloading image {message.id}...")
                    await message.download_media(file=image_path)

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(messages_data, f, ensure_ascii=False, indent=4, default=str)
    print(f"Saved {len(messages_data)} messages to {file_path}")

async def main():
    os.makedirs(DATA_LAKE_IMAGES_PATH, exist_ok=True)
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)

if __name__ == "__main__":
    asyncio.run(main())