-- models/marts/fct_image_detections.sql

with detections as (
    -- Get the cleaned detection data
    select * from {{ ref('stg_image_detections') }}
),

messages as (
    -- Get the message fact table, which contains our foreign keys
    select 
        message_id, 
        message_pk,
        channel_fk 
    from {{ ref('fct_messages') }}
)

select 
    -- Create a new primary key for this fact table
    {{ dbt_utils.generate_surrogate_key(['detections.message_id', 'detections.detected_object']) }} as image_detection_pk,

    -- Foreign keys to other tables
    messages.message_pk,
    messages.channel_fk,

    -- The actual facts from this table
    detections.detected_object,
    detections.confidence_score

from detections

-- Join back to the messages table to get the correct foreign keys
left join messages on detections.message_id = messages.message_id