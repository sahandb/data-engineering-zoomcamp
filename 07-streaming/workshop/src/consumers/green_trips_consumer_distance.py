"""
Homework Q3: count trips with trip_distance > 5 from topic `green-trips`.

  python src/consumers/green_trips_consumer_distance.py

Stops after several consecutive empty polls (producer finished / caught up).
"""

import json
import time

from kafka import KafkaConsumer

SERVER = "localhost:9092"
TOPIC = "green-trips"
GROUP_ID = "hw7-distance-count"
# ~3s of empty polls after the last record -> exit
EMPTY_POLLS_TO_STOP = 6
POLL_MS = 500


def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[SERVER],
        auto_offset_reset="earliest",
        group_id=f"{GROUP_ID}-{time.time_ns()}",
        enable_auto_commit=False,
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    while not consumer.assignment():
        consumer.poll(timeout_ms=POLL_MS)
    for tp in consumer.assignment():
        consumer.seek_to_beginning(tp)

    n = 0
    empty_streak = 0
    while empty_streak < EMPTY_POLLS_TO_STOP:
        batch = consumer.poll(timeout_ms=POLL_MS)
        if not batch:
            empty_streak += 1
            continue
        empty_streak = 0
        for _tp, records in batch.items():
            for msg in records:
                row = msg.value
                dist = row.get("trip_distance")
                if dist is not None and float(dist) > 5.0:
                    n += 1
    print(f"trips with trip_distance > 5: {n}")
    consumer.close()


if __name__ == "__main__":
    main()
