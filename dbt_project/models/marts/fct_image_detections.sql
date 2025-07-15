-- models/marts/fct_image_detections.sql

-- This model makes dbt aware of the fct_image_detections table,
-- which is populated by an external Python script (yolo_enricher.py).
-- We use an 'incremental' materialization with a 'false' condition to prevent dbt
-- from ever inserting data, while still allowing it to manage the table's existence.

{{
    config(
        materialized='incremental',
        unique_key='detection_pk'
    )
}}

-- The main body of the model will only be used to build the table
-- on the very first run, or if the table is dropped manually.
select
    CAST(null AS INTEGER) as detection_pk,
    CAST(null AS BIGINT) as message_fk,
    CAST(null AS VARCHAR) as detected_object_class,
    CAST(null AS FLOAT) as confidence_score

-- The 'is_incremental()' macro returns 'false' on the first run, building the table.
-- On subsequent runs, it returns 'true'. The 'where false' condition ensures
-- that dbt never attempts to insert or update any rows into this table,
-- leaving that responsibility to our Python script.
{% if is_incremental() %}
    where 1=0
{% endif %}