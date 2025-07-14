-- Final version

with messages as (
    select * from {{ ref('stg_telegram_messages') }}
),
channels as (
    select * from {{ ref('dim_channels') }}
)
select
    {{ dbt_utils.generate_surrogate_key(['messages.message_id']) }} as message_pk,
    channels.channel_pk as channel_fk, -- This is the line that was failing
    messages.message_id,
    messages.message_text,
    messages.view_count,
    messages.has_image,
    messages.posted_at
from 
    messages
left join channels on messages.channel_name = channels.channel_name