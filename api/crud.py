# api/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import text

# This function answers: "What are the top 10 most frequently mentioned products?"
# api/crud.py

from sqlalchemy.orm import Session
from sqlalchemy import text

def get_top_products(db: Session, limit: int = 10):
    """
    Finds the top N most frequently mentioned "products" by performing several
    text cleaning steps to filter out noise and common words.
    """
    
    # This query uses multiple CTEs to create a text cleaning pipeline in SQL.
    query = text("""
        WITH words AS (
            -- Step 1: Split all messages into individual words (tokens).
            -- The 'word' column will be our raw material.
            SELECT
                regexp_split_to_table(message_text, '\\s+') AS word
            FROM marts_analytics.fct_messages
        ),
        
        cleaned_words AS (
            -- Step 2: Clean each word.
            SELECT
                -- a. Convert to lowercase for case-insensitive counting.
                -- b. Use regexp_replace to remove all punctuation and special characters.
                --    '[^a-zA-Z]' matches any character that is NOT a letter.
                LOWER(regexp_replace(word, '[^a-zA-Z]', '', 'g')) as cleaned_word
            FROM words
        ),

        filtered_words AS (
            -- Step 3: Filter out meaningless words.
            SELECT cleaned_word
            FROM cleaned_words
            WHERE
                -- a. Filter out short words which are usually not product names.
                LENGTH(cleaned_word) > 3
                
                -- b. Filter out common English "stop words". This list can be expanded.
                AND cleaned_word NOT IN (
                    'the', 'for', 'and', 'are', 'with', 'you', 'this', 'that',
                    'from', 'call', 'have', 'more', 'free', 'price', 'delivery',
                    'contact', 'order', 'telegram', 'channel', 'available',
                    'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                    'saturday', 'sunday', 'until', 'adress', 'school'
                )
                
                -- c. Filter out words that are just numbers (if any slipped through).
                AND cleaned_word !~ '^[0-9\\.]+$'
        )

        -- Step 4: Count the frequencies of the remaining clean, filtered words.
        SELECT
            cleaned_word AS product,
            COUNT(*) AS mentions
        FROM filtered_words
        WHERE cleaned_word != '' -- Ensure we don't count empty strings from the cleaning step
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT :limit;
    """)
    
    result = db.execute(query, {"limit": limit}).fetchall()
    
    return [{"product": row[0], "mentions": row[1]} for row in result]

# ... your other functions ...

# ... rest of your file is likely okay, but I'll provide corrected versions just in case...

# This function answers: "What are the daily trends in posting volume?"
def get_channel_activity(db: Session, channel_name: str):
    # CORRECTED SCHEMA: Your dbt models are in 'marts_analytics' according to the error log
    query = text("""
        SELECT 
            c.channel_name,
            COUNT(f.message_pk) as post_count,
            DATE_TRUNC('day', f.posted_at)::date as activity_date
        FROM marts_analytics.fct_messages f
        JOIN marts_analytics.dim_channels c ON f.channel_fk = c.channel_pk
        WHERE c.channel_name = :channel_name
        GROUP BY c.channel_name, activity_date
        ORDER BY activity_date DESC;
    """)
    result = db.execute(query, {"channel_name": channel_name}).fetchall()
    return [{"channel": row[0], "post_count": row[1], "date": row[2]} for row in result]


# This function answers: "How does the availability of a product vary?" (by searching)
def search_messages(db: Session, keyword: str):
    # CORRECTED SCHEMA: Your dbt models are in 'marts_analytics'
    query = text("""
        SELECT
            f.message_pk,
            f.message_text,
            f.posted_at,
            c.channel_name
        FROM marts_analytics.fct_messages f
        JOIN marts_analytics.dim_channels c ON f.channel_fk = c.channel_pk
        WHERE f.message_text ILIKE :keyword
        ORDER BY f.posted_at DESC;
    """)
    result = db.execute(query, {"keyword": f"%{keyword}%"}).fetchall()
    return [{"message_id": row[0], "text": row[1], "posted_at": row[2], "channel": row[3]} for row in result]