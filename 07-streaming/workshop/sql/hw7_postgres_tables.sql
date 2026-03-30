-- Run before PyFlink jobs:
--   docker exec -i workshop-postgres-1 psql -U postgres -d postgres -f - < sql/hw7_postgres_tables.sql
-- Column names are lowercase so the PostgreSQL JDBC driver matches Flink’s INSERT statements.

DROP TABLE IF EXISTS hw7_tumble_5m_pu;
CREATE TABLE hw7_tumble_5m_pu (
    window_start TIMESTAMP(3) NOT NULL,
    pulocationid INT NOT NULL,
    num_trips BIGINT NOT NULL,
    PRIMARY KEY (window_start, pulocationid)
);

DROP TABLE IF EXISTS hw7_session_pu;
CREATE TABLE hw7_session_pu (
    window_start TIMESTAMP(3) NOT NULL,
    window_end TIMESTAMP(3) NOT NULL,
    pulocationid INT NOT NULL,
    num_trips BIGINT NOT NULL,
    PRIMARY KEY (window_start, window_end, pulocationid)
);

DROP TABLE IF EXISTS hw7_tip_hourly;
CREATE TABLE hw7_tip_hourly (
    window_start TIMESTAMP(3) NOT NULL PRIMARY KEY,
    total_tip DOUBLE PRECISION NOT NULL
);
