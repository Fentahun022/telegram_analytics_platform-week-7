-- models/marts/fct_messages.sql

/*
This is the main fact table for our star schema. Fact tables contain the
measurable events or "facts" of a business process. In this case, each row
represents a single message being posted.

Key responsibilities:
1.  Join message data from the staging layer with the channel dimension.
2.  Replace the natural keys (like channel_name) with the stable surrogate keys (channel_fk) from the dimension tables.
3.  Store key metrics (facts) like `view_count`.
4.  Keep important descriptive attributes (degenerate dimensions) like `message_text`.
*/

with messages as (
    -- This CTE gets our core message data from the staging layer.
    select * from {{ ref('stg_telegram_messages') }}
),

channels as (
    -- This CTE gets our channel dimension data, which contains the surrogate primary key.
    select * from {{ ref('dim_channels') }}
)

select
    -- Create a unique surrogate primary key for this fact table.
    {{ dbt_utils.generate_surrogate_key(['messages.message_id']) }} as message_pk,
    
    -- Foreign Key (FK) to the channel dimension table. This links the fact to its dimension.
    channels.channel_pk as channel_fk,
    
    -- The original message_id is kept as a "degenerate dimension". This is a descriptive
    -- attribute that lives in the fact table because it has no other attributes
    -- to form its own dimension table (e.g., no message_creation_user, etc.).
    messages.message_id,

    -- The core facts and attributes of the message event.
    messages.message_text,
    messages.view_count,
    messages.has_image,
    messages.posted_at
    
from 
    messages
-- Join the messages to the channels on their common business key (`channel_name`)
-- to find the correct surrogate key (`channel_pk`) for each message.
left join channels on messages.channel_name = channels.channel_name