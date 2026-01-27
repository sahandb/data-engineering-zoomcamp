# Module 1 Homework: Docker & SQL

This repository contains solutions to the Module 1 homework questions.

## Question 1: Understanding Docker images

**Task:** Run docker with the python:3.13 image. Use an entrypoint bash to interact with the container. What's the version of pip in the image?

### Shell Command:
```bash
docker run --entrypoint bash python:3.13 -c "pip --version"
```

Or interactively:
```bash
docker run -it --entrypoint bash python:3.13
# Then inside the container: pip --version
```

**Answer:** Check the output of the command above.

---

## Question 2: Understanding Docker networking

**Task:** Given the docker-compose.yaml, what is the hostname and port that pgadmin should use to connect to the postgres database?

### Explanation:
In Docker Compose, services communicate using their **service names** as hostnames. The service name is `db`.

For ports:
- Inside the container, postgres runs on port `5432` (default PostgreSQL port)
- The port mapping `5433:5432` maps host port 5433 to container port 5432
- **For inter-container communication**, use the **container's internal port** (5432), not the host-mapped port (5433)

**Answer: `db:5432`**

---

## Question 3: Counting short trips

**Task:** For trips in November 2025 (lpep_pickup_datetime between '2025-11-01' and '2025-12-01', exclusive of the upper bound), how many trips had a trip_distance of less than or equal to 1 mile?

### Download Data:
```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

### SQL Query:
```sql
SELECT COUNT(*) as short_trips_count
FROM green_taxi_trips
WHERE lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1.0;
```

**Answer:** Run the query to get the count.

---

## Question 4: Longest trip for each day

**Task:** Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles (to exclude data errors). Use the pick up time for your calculations.

### SQL Query:
```sql
SELECT 
    DATE(lpep_pickup_datetime) as pickup_date,
    MAX(trip_distance) as max_distance
FROM green_taxi_trips
WHERE lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance < 100
GROUP BY DATE(lpep_pickup_datetime)
ORDER BY max_distance DESC
LIMIT 1;
```

**Answer:** Check the pickup_date from the query result.

---

## Question 5: Biggest pickup zone

**Task:** Which was the pickup zone with the largest total_amount (sum of all trips) on November 18th, 2025?

### SQL Query:
```sql
SELECT 
    z.Zone as pickup_zone,
    SUM(t.total_amount) as total_amount_sum
FROM green_taxi_trips t
JOIN taxi_zone_lookup z ON t.PULocationID = z.LocationID
WHERE DATE(t.lpep_pickup_datetime) = '2025-11-18'
GROUP BY z.Zone
ORDER BY total_amount_sum DESC
LIMIT 1;
```

**Answer:** Check the pickup_zone from the query result.

---

## Question 6: Largest tip

**Task:** For passengers picked up in the zone named "East Harlem North" in November 2025, which was the drop off zone that had the largest tip?

**Note:** It's tip, not trip. We need the name of the zone, not the ID.

### SQL Query:
```sql
SELECT 
    z_dropoff.Zone as dropoff_zone,
    SUM(t.tip_amount) as total_tips
FROM green_taxi_trips t
JOIN taxi_zone_lookup z_pickup ON t.PULocationID = z_pickup.LocationID
JOIN taxi_zone_lookup z_dropoff ON t.DOLocationID = z_dropoff.LocationID
WHERE t.lpep_pickup_datetime >= '2025-11-01' 
  AND t.lpep_pickup_datetime < '2025-12-01'
  AND z_pickup.Zone = 'East Harlem North'
GROUP BY z_dropoff.Zone
ORDER BY total_tips DESC
LIMIT 1;
```

**Answer:** Check the dropoff_zone from the query result.

---

## Question 7: Terraform Workflow

**Task:** Which sequence describes the workflow for:
1. Downloading the provider plugins and setting up backend
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform

### Explanation:

1. **Downloading provider plugins and setting up backend:** `terraform init`
   - Initializes Terraform working directory
   - Downloads provider plugins
   - Sets up backend configuration

2. **Generating proposed changes and auto-executing the plan:** `terraform apply -auto-approve`
   - Generates execution plan
   - Automatically approves and applies changes

3. **Remove all resources managed by terraform:** `terraform destroy`
   - Destroys all resources managed by the current Terraform configuration

**Answer: `terraform init, terraform apply -auto-approve, terraform destroy`**

---

## Setup Instructions

### Prerequisites:
- Docker installed
- PostgreSQL client (or use pgAdmin)
- Python 3.x with pandas and pyarrow (for notebook analysis)

### Running the Analysis:

1. **Download the data:**
   ```bash
   wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
   wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
   ```

2. **Set up PostgreSQL database:**
   - Use docker-compose or run PostgreSQL container
   - Import the parquet data and CSV file into PostgreSQL
   - Run the SQL queries provided above

3. **Or use the Jupyter notebook:**
   - Open `HW1.ipynb`
   - Run all cells to perform the analysis using pandas

---

## Notes

- All SQL queries assume the table names are `green_taxi_trips` and `taxi_zone_lookup`
- Make sure to import the data into PostgreSQL before running SQL queries
- The notebook provides Python/pandas alternatives for all SQL-based questions
