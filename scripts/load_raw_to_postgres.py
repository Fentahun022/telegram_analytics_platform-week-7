import os
import json
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
import logging

# --- Configuration ---
# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# --- Database Connection Details from .env ---
# IMPORTANT: When running this script from your local machine (not in Docker),
# the DB_HOST is 'localhost'. When running inside the Docker container, it's 'db'.
DB_HOST = os.getenv("DB_HOST", "localhost") 
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = os.getenv("DB_PORT", "5432")

# --- Data Location ---
RAW_MESSAGES_PATH = 'data/raw/telegram_messages'


def get_db_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logging.info("Successfully connected to the database.")
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Could not connect to the database: {e}")
        return None

def setup_database(cursor):
    """Ensures the necessary schema and table exist."""
    logging.info("Setting up database schema and table...")
    
    # Create the 'raw' schema if it doesn't exist
    cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    
    # Create the 'telegram_messages' table if it doesn't exist
    # Using JSONB is highly recommended for performance and query capabilities.
    # The PRIMARY KEY on message_id is CRITICAL for idempotency.
    create_table_query = """
    CREATE TABLE IF NOT EXISTS raw.telegram_messages (
        message_id BIGINT PRIMARY KEY,
        channel_name VARCHAR(255),
        raw_message JSONB,
        loaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    cursor.execute(create_table_query)
    logging.info("Database setup complete.")


def process_and_load_data(conn):
    """Finds JSON files, processes them, and loads data into the database."""
    processed_files = 0
    total_messages_upserted = 0
    
    with conn.cursor() as cursor:
        # Walk through the directory to find all JSON files
        for root, _, files in os.walk(RAW_MESSAGES_PATH):
            for filename in files:
                if filename.endswith('.json'):
                    file_path = os.path.join(root, filename)
                    logging.info(f"Processing file: {file_path}")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            messages = json.load(f)
                        
                        channel_name = os.path.splitext(filename)[0]
                        messages_in_file = 0
                        
                        for message in messages:
                            message_id = message.get('id')
                            if not message_id:
                                logging.warning(f"Skipping message without ID in file {filename}")
                                continue
                            
                            # This is the idempotent part: ON CONFLICT DO UPDATE
                            # It tries to insert. If a row with the same message_id exists,
                            # it updates the existing row instead of creating a duplicate.
                            upsert_query = """
                            INSERT INTO raw.telegram_messages (message_id, channel_name, raw_message)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (message_id) DO UPDATE SET
                                raw_message = EXCLUDED.raw_message,
                                loaded_at = NOW();
                            """
                            # Use psycopg2.extras.Json to correctly handle JSON data
                            cursor.execute(upsert_query, (message_id, channel_name, Json(message)))
                            messages_in_file += 1
                        
                        logging.info(f"  -> Upserted {messages_in_file} messages for channel '{channel_name}'.")
                        total_messages_upserted += messages_in_file
                        processed_files += 1
                        
                    except json.JSONDecodeError:
                        logging.error(f"Could not decode JSON from file: {file_path}")
                    except Exception as e:
                        logging.error(f"An error occurred while processing {file_path}: {e}")
    
    conn.commit()
    logging.info(f"\n--- Load Complete ---")
    logging.info(f"Processed {processed_files} files.")
    logging.info(f"Total messages upserted: {total_messages_upserted}.")


def main():
    """Main function to run the data loading process."""
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                setup_database(cursor)
            conn.commit() # Commit the setup changes
            
            process_and_load_data(conn)
            
        finally:
            conn.close()
            logging.info("Database connection closed.")


if __name__ == "__main__":
    main()