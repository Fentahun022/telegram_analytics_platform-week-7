import os
import json
import asyncio
from telethon import TelegramClient
from datetime import datetime
from dotenv import load_dotenv

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_NAME = 'telegram_scraper' # This will create a file named telegram_scraper.session

# List of target public Telegram channels
CHANNELS = [
    'lobelia4cosmetics',
    'tikvahpharma',
    'CheMed123', # Another example channel
    # Add more channels from https://et.tgstat.com/medicine
]

DATA_LAKE_MESSAGES_PATH = 'data/raw/telegram_messages'
DATA_LAKE_IMAGES_PATH = 'data/raw/telegram_images'

# --- Main Logic ---

async def scrape_channel(client, channel_name):
    """Scrapes a single channel and saves messages and images."""
    today = datetime.now().strftime('%Y-%m-%d')
    output_dir = os.path.join(DATA_LAKE_MESSAGES_PATH, today)
    os.makedirs(output_dir, exist_ok=True)

    file_path = os.path.join(output_dir, f"{channel_name}.json")
    messages_data = []

    print(f"Scraping channel: {channel_name}")
    try:
        # Get the channel entity to make sure it exists
        channel_entity = await client.get_entity(channel_name)
        
        # Iterate through messages, limit can be adjusted
        async for message in client.iter_messages(channel_entity, limit=200):
            if message.text or message.photo:
                # Convert message object to a dictionary for JSON serialization
                message_dict = message.to_dict()
                messages_data.append(message_dict)

                # Download image if it exists and we don't have it yet
                if message.photo:
                    image_path = os.path.join(DATA_LAKE_IMAGES_PATH, f"{message.id}.jpg")
                    if not os.path.exists(image_path):
                        print(f"  -> Downloading image for message {message.id}...")
                        await message.download_media(file=image_path)
    except Exception as e:
        print(f"  [ERROR] Could not scrape channel '{channel_name}': {e}")
        return

    # Save the collected message data to a JSON file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(messages_data, f, ensure_ascii=False, indent=4, default=str)
    
    print(f"  -> Saved {len(messages_data)} messages to {file_path}")

async def main():
    """Main function to initialize client and start scraping."""
    # Create the data directories if they don't exist
    os.makedirs(DATA_LAKE_IMAGES_PATH, exist_ok=True)
    
    # The 'async with' block handles connecting and disconnecting automatically
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)
    
    print("\nScraping session finished.")

if __name__ == "__main__":
    # This ensures the async main function is run correctly
    asyncio.run(main())