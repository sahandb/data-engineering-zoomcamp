-- Staging model for For-Hire Vehicle (FHV) trip data (HW4 Q6)
-- Filters out records where dispatching_base_num IS NULL
-- Renames columns to snake_case to match project conventions

with source as (
    select * from {{ source('raw', 'fhv_tripdata') }}
),

renamed as (
    select
        cast(dispatching_base_num as string) as dispatching_base_num,
        cast(pulocationid as integer) as pickup_location_id,
        cast(dolocationid as integer) as dropoff_location_id,
        cast(pickup_datetime as timestamp) as pickup_datetime,
        cast(dropoff_datetime as timestamp) as dropoff_datetime,
        cast(sr_flag as integer) as sr_flag,
        cast(affiliated_base_number as string) as affiliated_base_number
    from source
    where dispatching_base_num is not null
)

select * from renamed
