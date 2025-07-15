from sqlalchemy.orm import Session
from sqlalchemy import text, func

# This function answers: "What are the top 10 most frequently mentioned products?"
def get_top_products(db: Session, limit: int = 10):
    # This is a simplified keyword search. A more advanced version would use NLP.
    # Note: We query the 'marts' schema where our dbt models live.
    query = text("""
        SELECT
            LOWER(regexp_split_to_table(message_text, '\\s+')) AS product,
            COUNT(*) AS mentions
        FROM marts.fct_messages
        WHERE LENGTH(regexp_split_to_table(message_text, '\\s+')) > 4 -- Filter short words
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT :limit;
    """)
    result = db.execute(query, {"limit": limit}).fetchall()
    return [{"product": row[0], "mentions": row[1]} for row in result]

# This function answers: "What are the daily trends in posting volume?"
def get_channel_activity(db: Session, channel_name: str):
    query = text("""
        SELECT 
            c.channel_name,
            COUNT(f.message_id) as post_count
        FROM marts.fct_messages f
        JOIN marts.dim_channels c ON f.channel_fk = c.channel_pk
        WHERE c.channel_name = :channel_name
        GROUP BY c.channel_name;
    """)
    result = db.execute(query, {"channel_name": channel_name}).fetchone()
    return result

# This function answers: "How does the availability of a product vary?" (by searching)
def search_messages(db: Session, keyword: str):
    query = text("""
        SELECT
            f.message_id,
            f.message_text,
            f.posted_at,
            c.channel_name
        FROM marts.fct_messages f
        JOIN marts.dim_channels c ON f.channel_fk = c.channel_pk
        WHERE f.message_text ILIKE :keyword
        ORDER BY f.posted_at DESC;
    """)
    result = db.execute(query, {"keyword": f"%{keyword}%"}).fetchall()
    return result