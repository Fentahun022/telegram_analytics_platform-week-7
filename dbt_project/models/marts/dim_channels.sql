-- models/marts/dim_channels.sql

select
    -- Use dbt_utils to create a unique, consistent primary key (PK) for the channel dimension.
    -- This key is based on the channel's business key, which is its name.
    {{ dbt_utils.generate_surrogate_key(['channel_name']) }} as channel_pk,

    channel_name,
    channel_id -- It's good practice to keep the original source ID as well
    
from {{ ref('stg_telegram_messages') }}

-- Use group by to ensure we only get one row per channel
group by
    channel_name,
    channel_id