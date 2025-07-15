-- models/staging/stg_telegram_messages.sql

with source as (

    -- CORRECT: Use the source() macro to build the dependency graph
    select * from {{ source('raw_telegram', 'telegram_messages') }}

)

select
    -- CORRECT: Use the ->> operator to extract fields as text from the JSONB column
    -- The raw data is in the 'raw_message' column from our loader script
    (raw_message ->> 'id')::bigint as message_id,
    
    -- CORRECT: To access nested JSON, chain the operators
    (raw_message -> 'peer_id' ->> 'channel_id')::bigint as channel_id,

    -- This column comes directly from our loader script, no JSON parsing needed
    channel_name,
    
    -- The 'date' field in the JSON is a timestamp string
    (raw_message ->> 'date')::timestamp as posted_at,
    
    (raw_message ->> 'views')::integer as view_count,
    
    raw_message ->> 'message' as message_text,
    
    
    (raw_message -> 'photo') is not null as has_image

from source
where 
   
    raw_message ->> 'message' is not null 
    and raw_message ->> 'message' != ''