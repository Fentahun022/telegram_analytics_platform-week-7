-- models/marts/fct_image_detections.sql

with detections as (
    -- This should reference a staging model for your YOLO results
    select * from {{ ref('stg_image_detections') }} 
),
messages as (
    -- We need fct_messages to get the foreign keys
    select message_id, channel_fk from {{ ref('fct_messages') }}
)
select 
    detections.message_id,
    messages.channel_fk, -- <-- CORRECT: Get the foreign key from the messages fact table
    detections.detected_object,
    detections.confidence_score

from detections
-- Join to the messages fact table on the shared message_id
left join messages on detections.message_id = messages.message_id