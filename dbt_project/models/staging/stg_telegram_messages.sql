-- dbt_project/models/staging/stg_telegram_messages.sql
select
    CAST(JSON_VALUE(message_data, '$.id') AS BIGINT) as message_id,
    CAST(JSON_VALUE(message_data, '$.peer_id.channel_id') AS BIGINT) as channel_id,
    channel_name,
    CAST(JSON_VALUE(message_data, '$.date') AS TIMESTAMP) as message_timestamp,
    CAST(JSON_VALUE(message_data, '$.views') AS INTEGER) as views,
    JSON_VALUE(message_data, '$.message') as message_text,
    (JSON_VALUE(message_data, '$.media') is not null) as has_media,
    JSON_VALUE(message_data, '$.image_path') as image_path
from
    public.raw_telegram_messages