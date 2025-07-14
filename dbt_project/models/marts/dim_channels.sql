-- models/marts/dim_channels.sql

/*
This model creates the dimension table for Telegram channels.
Dimension tables provide descriptive context to the data in fact tables.

Key responsibilities:
1.  Create a unique, stable primary key (`channel_pk`) for each channel. This is known as a surrogate key.
2.  Provide a clean list of all unique channels, avoiding duplication.
3.  Keep the original source ID (`channel_id`) for traceability.
*/

select
    -- Use dbt_utils.generate_surrogate_key to create a hashed, deterministic primary key
    -- based on the channel's business key (its unique name). This ensures the key is always
    -- the same for the same channel name, making joins reliable.
    {{ dbt_utils.generate_surrogate_key(['channel_name']) }} as channel_pk,

    -- The human-readable name of the channel.
    channel_name,

    -- The original numeric ID from Telegram. It's good practice to keep this
    -- for potential joins back to raw data or for debugging.
    channel_id
    
from 
    -- We build our dimension directly from the clean, staged data.
    {{ ref('stg_telegram_messages') }}

-- Use GROUP BY to ensure we only get one unique row per channel.
-- `distinct` would also work, but `group by` is often clearer when aggregating.
group by
    channel_name,
    channel_id