-- models/staging/stg_telegram_messages.sql

/*
This staging model is the first layer of transformation on the raw Telegram data.
Its purpose is to:
1.  Select from the raw source table (`raw.telegram_messages`).
2.  Extract key fields from the raw_message JSONB column.
3.  Cast fields to their correct data types (e.g., BIGINT, TIMESTAMP).
4.  Perform basic cleaning by filtering out messages without text.
This model provides a clean, structured base for all downstream models.
*/

with source as (

    -- Use the source() macro to create a dependency on the raw table.
    -- This allows dbt to track lineage and manage dependencies automatically.
    select * from {{ source('raw_telegram', 'telegram_messages') }}

)

select
    -- The message_id is the unique natural key for each message from Telegram.
    (raw_message ->> 'id')::bigint as message_id,
    
    -- To access nested JSON, we chain the operators. 'peer_id' is an object containing 'channel_id'.
    (raw_message -> 'peer_id' ->> 'channel_id')::bigint as channel_id,

    -- The channel_name was added during the initial Python loading script.
    channel_name,
    
    -- The 'date' field in the JSON is a UTC timestamp string that needs to be cast.
    (raw_message ->> 'date')::timestamp as posted_at,
    
    -- Views provide a metric for message popularity.
    (raw_message ->> 'views')::integer as view_count,
    
    -- The core text content of the message. The ->> operator extracts it as text.
    raw_message ->> 'message' as message_text,
    
    -- A boolean flag to easily identify messages containing images, useful for visual content analysis.
    (raw_message -> 'photo') is not null as has_image

from source
where 
    -- Basic data quality filter: we are only interested in messages that contain text.
    raw_message ->> 'message' is not null 
    and raw_message ->> 'message' != ''