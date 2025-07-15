# scripts/run_yolo_enrichment.py
import os, psycopg2, logging
from ultralytics import YOLO
from dotenv import load_dotenv

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = os.getenv("DB_PORT", "5433")
DATA_LAKE_IMAGES_PATH = 'data/raw/telegram_images'

def get_db_connection():
    try:
        return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    except psycopg2.OperationalError as e:
        logging.error(f"Could not connect to database: {e}")
        return None

def setup_yolo_table(cursor):
    cursor.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw.image_detections (
        message_id BIGINT,
        detected_object VARCHAR(255),
        confidence_score REAL,
        detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        PRIMARY KEY (message_id, detected_object)
    );
    """)
    logging.info("Table 'raw.image_detections' is ready.")

def enrich_images():
    conn = get_db_connection()
    if not conn: return

    try:
        with conn.cursor() as cur:
            setup_yolo_table(cur)
            conn.commit()

            logging.info("Loading YOLOv8 model...")
            model = YOLO('yolov8n.pt') # 'n' for nano is small and fast

            image_files = [f for f in os.listdir(DATA_LAKE_IMAGES_PATH) if f.endswith('.jpg')]
            logging.info(f"Found {len(image_files)} images to process.")

            for image_file in image_files:
                image_path = os.path.join(DATA_LAKE_IMAGES_PATH, image_file)
                message_id = int(os.path.splitext(image_file)[0])

                results = model(image_path, verbose=False) # verbose=False cleans up console output

                for r in results:
                    for box in r.boxes:
                        class_name = model.names[int(box.cls)]
                        confidence = float(box.conf)

                        if confidence > 0.45: # Confidence threshold
                            logging.info(f"  -> Detected '{class_name}' in image for message {message_id} (confidence: {confidence:.2f})")
                            cur.execute("""
                                INSERT INTO raw.image_detections (message_id, detected_object, confidence_score)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (message_id, detected_object) DO NOTHING;
                            """, (message_id, class_name, confidence))
            conn.commit()
    finally:
        conn.close()
    logging.info("Image enrichment process finished.")

if __name__ == "__main__":
    enrich_images()