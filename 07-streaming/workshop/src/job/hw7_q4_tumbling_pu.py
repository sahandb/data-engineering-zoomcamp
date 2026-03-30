"""
Homework Q4: 5-minute tumbling windows — trip count per PULocationID.

Submit:
  docker exec -it workshop-jobmanager-1 flink run -py /opt/src/job/hw7_q4_tumbling_pu.py

Create sink table in PostgreSQL first (see sql/hw7_postgres_tables.sql).
"""

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import EnvironmentSettings, StreamTableEnvironment


def create_green_trips_source(t_env):
    table_name = "green_trips"
    ddl = f"""
        CREATE TABLE {table_name} (
            lpep_pickup_datetime VARCHAR,
            lpep_dropoff_datetime VARCHAR,
            PULocationID INT,
            DOLocationID INT,
            passenger_count DOUBLE,
            trip_distance DOUBLE,
            tip_amount DOUBLE,
            total_amount DOUBLE,
            event_timestamp AS TO_TIMESTAMP(lpep_pickup_datetime, 'yyyy-MM-dd HH:mm:ss'),
            WATERMARK FOR event_timestamp AS event_timestamp - INTERVAL '5' SECOND
        ) WITH (
            'connector' = 'kafka',
            'properties.bootstrap.servers' = 'redpanda:29092',
            'topic' = 'green-trips',
            'scan.startup.mode' = 'earliest-offset',
            'properties.auto.offset.reset' = 'earliest',
            'format' = 'json'
        );
        """
    t_env.execute_sql(ddl)
    return table_name


def create_sink(t_env):
    table_name = "hw7_tumble_5m_pu"
    ddl = f"""
        CREATE TABLE {table_name} (
            window_start TIMESTAMP(3),
            pulocationid INT,
            num_trips BIGINT,
            PRIMARY KEY (window_start, pulocationid) NOT ENFORCED
        ) WITH (
            'connector' = 'jdbc',
            'url' = 'jdbc:postgresql://postgres:5432/postgres',
            'table-name' = '{table_name}',
            'username' = 'postgres',
            'password' = 'postgres',
            'driver' = 'org.postgresql.Driver'
        );
        """
    t_env.execute_sql(ddl)
    return table_name


def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(10 * 1000)
    env.set_parallelism(1)

    settings = EnvironmentSettings.new_instance().in_streaming_mode().build()
    t_env = StreamTableEnvironment.create(env, environment_settings=settings)

    src = create_green_trips_source(t_env)
    sink = create_sink(t_env)

    t_env.execute_sql(
        f"""
        INSERT INTO {sink}
        SELECT
            window_start,
            PULocationID AS pulocationid,
            CAST(COUNT(*) AS BIGINT) AS num_trips
        FROM TABLE(
            TUMBLE(TABLE {src}, DESCRIPTOR(event_timestamp), INTERVAL '5' MINUTE)
        )
        GROUP BY window_start, PULocationID;
        """
    ).wait()


if __name__ == "__main__":
    main()
