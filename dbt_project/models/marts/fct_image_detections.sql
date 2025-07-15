

with detections as (
  
    select * from {{ ref('stg_image_detections') }}
),

messages as (
    -- Get the message fact table, which contains our necessary primary and foreign keys
    select 
        message_id, 
        message_pk,
        channel_fk 
    from {{ ref('fct_messages') }}
)

select 
    -- CORRECT: Create a new surrogate primary key for this fact table.
    -- This ensures every row (a unique object detection in a unique message) is identifiable.
    {{ dbt_utils.generate_surrogate_key(['detections.message_id', 'detections.detected_object']) }} as image_detection_pk,

    -- CORRECT: Select the foreign key to the messages table.
    messages.message_pk,
    
    -- CORRECT: Select the foreign key to the channels table.
    messages.channel_fk,

    -- The actual facts from this table
    detections.detected_object,
    detections.confidence_score

from detections

-- Join back to the messages table on the natural key to get the correct surrogate keys
left join messages on detections.message_id = messages.message_id
where
    -- Data quality check: ensure the join was successful. This prevents orphan records
    -- in the image detections fact table.
    messages.message_pk is not null