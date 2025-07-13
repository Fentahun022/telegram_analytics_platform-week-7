with messages as (
    select * from {{ ref('stg_telegram_messages') }}
),

channels as (
    select
        channel_id,
        row_number() over (order by channel_id) as channel_pk -- Surrogate key
    from {{ ref('dim_channels') }}
)

select
    m.message_id as message_pk,
    c.channel_pk as channel_fk,
    m.message_timestamp,
    m.message_text,
    m.views as view_count,
    length(m.message_text) as message_length,
    m.has_media as has_image,
    m.image_path
from messages m
left join channels c on m.channel_id = c.channel_id