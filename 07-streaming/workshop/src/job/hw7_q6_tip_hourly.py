"""
Homework Q6: 1-hour tumbling windows — total tip_amount per hour (all locations).

Submit:
  docker exec -it workshop-jobmanager-1 flink run -py /opt/src/job/hw7_q6_tip_hourly.py
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
    table_name = "hw7_tip_hourly"
    ddl = f"""
        CREATE TABLE {table_name} (
            window_start TIMESTAMP(3),
            total_tip DOUBLE,
            PRIMARY KEY (window_start) NOT ENFORCED
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
            SUM(tip_amount) AS total_tip
        FROM TABLE(
            TUMBLE(TABLE {src}, DESCRIPTOR(event_timestamp), INTERVAL '1' HOUR)
        )
        GROUP BY window_start;
        """
    ).wait()


if __name__ == "__main__":
    main()
