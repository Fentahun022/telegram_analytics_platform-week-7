select
    distinct
    channel_id,
    channel_name
from {{ ref('stg_telegram_messages') }}