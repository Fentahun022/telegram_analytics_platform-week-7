-- models/staging/stg_image_detections.sql

select
    message_id,
    detected_object,
    confidence_score

from {{ source('raw_telegram', 'image_detections') }}