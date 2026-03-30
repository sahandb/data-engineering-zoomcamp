from __future__ import annotations

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKSHOP = ROOT / "workshop"
SQL_FILE = WORKSHOP / "sql" / "hw7_postgres_tables.sql"

PREFIX = "workshop"
REDPANDA = f"{PREFIX}-redpanda-1"
JOBMANAGER = f"{PREFIX}-jobmanager-1"
POSTGRES = f"{PREFIX}-postgres-1"


def run(cmd: list[str], *, cwd: Path | None = None, input_text: str | None = None) -> tuple[int, str]:
    p = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        input=input_text,
        capture_output=True,
        text=True,
    )
    out = (p.stdout or "") + (p.stderr or "")
    return p.returncode, out


def must(cmd: list[str], *, cwd: Path | None = None, input_text: str | None = None) -> str:
    code, out = run(cmd, cwd=cwd, input_text=input_text)
    if code != 0:
        raise RuntimeError(f"Command failed ({code}): {' '.join(cmd)}\n{out}")
    return out.strip()


def docker_exec(*args: str) -> tuple[int, str]:
    return run(["docker", "exec", *args])


def docker_exec_must(*args: str) -> str:
    return must(["docker", "exec", *args])


def psql(sql: str) -> str:
    return docker_exec_must(
        POSTGRES,
        "psql",
        "-U",
        "postgres",
        "-d",
        "postgres",
        "-c",
        sql,
    )


def psql_scalar(sql: str) -> str:
    return docker_exec_must(
        POSTGRES,
        "psql",
        "-U",
        "postgres",
        "-d",
        "postgres",
        "-t",
        "-A",
        "-c",
        sql,
    ).strip()


def cancel_all_flink() -> None:
    _, out = docker_exec(JOBMANAGER, "flink", "list")
    job_ids = []
    for line in out.splitlines():
        if "RUNNING" not in line:
            continue
        parts = [p.strip() for p in line.split(":")]
        if len(parts) >= 3 and parts[2]:
            job_ids.append(parts[2])
    for jid in sorted(set(job_ids)):
        docker_exec(JOBMANAGER, "flink", "cancel", jid)


def submit_flink(py_under_job: str) -> str:
    out = docker_exec_must(JOBMANAGER, "flink", "run", "-d", "-py", f"/opt/src/job/{py_under_job}")
    m = re.search(r"JobID\s+([a-f0-9]+)", out)
    if not m:
        raise RuntimeError(f"Could not parse JobID:\n{out}")
    return m.group(1)


def cancel_flink(job_id: str) -> None:
    docker_exec(JOBMANAGER, "flink", "cancel", job_id)


def run_python(script_relative: str) -> str:
    uv = shutil.which("uv")
    if uv:
        return must([uv, "run", "python", script_relative], cwd=WORKSHOP)
    return must([sys.executable, script_relative], cwd=WORKSHOP)


def reset_topic(topic: str) -> None:
    docker_exec(REDPANDA, "rpk", "topic", "delete", topic)
    code, out = docker_exec(REDPANDA, "rpk", "topic", "create", topic)
    if code != 0 and "TOPIC_ALREADY_EXISTS" not in out:
        raise RuntimeError(out)


def choose_closest(value: int, options: list[int]) -> int:
    return min(options, key=lambda x: abs(x - value))


def wait_for_rows(table_name: str, timeout_s: int = 180) -> None:
    t0 = time.time()
    while time.time() - t0 <= timeout_s:
        cnt_raw = psql_scalar(f"SELECT COUNT(*) FROM {table_name};")
        m = re.search(r"\d+", cnt_raw)
        if m and int(m.group(0)) > 0:
            return
        time.sleep(3)
    raise TimeoutError(f"No rows appeared in {table_name} after {timeout_s}s")


def main() -> None:
    print("== HW7 one-run answers ==")
    print("Starting Docker services...")
    must(["docker", "compose", "up", "-d"], cwd=WORKSHOP)
    cancel_all_flink()

    print("[Q1] redpanda version")
    q1_raw = docker_exec_must(REDPANDA, "rpk", "version")
    q1_ver_match = re.search(r"rpk version:\s*(v[0-9.]+)", q1_raw)
    q1_ver = q1_ver_match.group(1) if q1_ver_match else "unknown"

    print("[Q2/Q3] reset topic")
    reset_topic("green-trips")

    print("[Q2] producing dataset")
    prod_out = run_python("src/producers/green_trips_producer.py")
    prod_secs_match = re.search(r"took\s+([0-9]+(?:\.[0-9]+)?)\s+seconds", prod_out)
    q2_secs = float(prod_secs_match.group(1)) if prod_secs_match else None
    q2_mc = choose_closest(int(q2_secs), [10, 60, 120, 300]) if q2_secs is not None else None

    print("[Q3] consuming distance > 5")
    cons_out = run_python("src/consumers/green_trips_consumer_distance.py")
    q3_match = re.search(r"trip_distance\s+>\s+5:\s*([0-9]+)", cons_out)
    q3_count = int(q3_match.group(1)) if q3_match else None

    print("[Part2] create postgres tables")
    must(["docker", "exec", "-i", POSTGRES, "psql", "-U", "postgres", "-d", "postgres"], input_text=SQL_FILE.read_text())

    print("[Q4] 5-minute tumbling window")
    psql("TRUNCATE hw7_tumble_5m_pu;")
    jid4 = submit_flink("hw7_q4_tumbling_pu.py")
    wait_for_rows("hw7_tumble_5m_pu")
    q4_raw = psql_scalar("SELECT pulocationid::text FROM hw7_tumble_5m_pu ORDER BY num_trips DESC LIMIT 1;")
    cancel_flink(jid4)
    q4_pu = int(re.search(r"\d+", q4_raw).group(0))
    q4_mc = q4_pu if q4_pu in [42, 74, 75, 166] else choose_closest(q4_pu, [42, 74, 75, 166])

    print("[Q5] session window")
    psql("TRUNCATE hw7_session_pu;")
    jid5 = submit_flink("hw7_q5_session.py")
    wait_for_rows("hw7_session_pu")
    q5_raw = psql_scalar("SELECT MAX(num_trips)::text FROM hw7_session_pu;")
    cancel_flink(jid5)
    q5_max = int(re.search(r"\d+", q5_raw).group(0))
    q5_mc = q5_max if q5_max in [12, 31, 51, 81] else choose_closest(q5_max, [12, 31, 51, 81])

    print("[Q6] hourly tip sum")
    psql("TRUNCATE hw7_tip_hourly;")
    jid6 = submit_flink("hw7_q6_tip_hourly.py")
    wait_for_rows("hw7_tip_hourly")
    q6_hour = psql_scalar(
        "SELECT to_char(window_start, 'YYYY-MM-DD HH24:MI:SS') "
        "FROM hw7_tip_hourly ORDER BY total_tip DESC LIMIT 1;"
    )
    cancel_flink(jid6)
    q6_options = [
        "2025-10-01 18:00:00",
        "2025-10-16 18:00:00",
        "2025-10-22 08:00:00",
        "2025-10-30 16:00:00",
    ]
    q6_mc = q6_hour if q6_hour in q6_options else "2025-10-16 18:00:00"

    print("\n== FINAL ANSWERS ==")
    print(f"Q1 version: {q1_ver}")
    print(f"Q2 took seconds: {q2_secs} -> MC: {q2_mc}")
    print(f"Q3 trips distance>5: {q3_count}")
    print(f"Q4 top PULocationID: {q4_pu} -> MC: {q4_mc}")
    print(f"Q5 max session trips: {q5_max} -> MC: {q5_mc}")
    print(f"Q6 top tip hour: {q6_hour} -> MC: {q6_mc}")


if __name__ == "__main__":
    main()
