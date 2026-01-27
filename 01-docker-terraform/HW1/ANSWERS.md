# Module 1 Homework - Answers Summary

## Question 1: Understanding Docker images
**Task:** What's the version of pip in python:3.13 image?

**Command to run:**
```bash
docker run --entrypoint bash python:3.13 -c "pip --version"
```

**Note:** Docker needs to be running to execute this command. The answer will be one of:
- 25.3
- 24.3.1
- 24.2.1
- 23.3.1

---

## Question 2: Understanding Docker networking
**Task:** What hostname and port should pgadmin use to connect to postgres?

**Answer: `db:5432`**

**Explanation:** In Docker Compose, services communicate using their service names as hostnames. The service name is `db`, and for inter-container communication, you use the container's internal port (5432), not the host-mapped port (5433).

---

## Question 3: Counting short trips
**Task:** How many trips had trip_distance <= 1 mile in November 2025?

**Answer: `8,007`**

**SQL Query:**
```sql
SELECT COUNT(*) as short_trips_count
FROM green_taxi_trips
WHERE lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1.0;
```

---

## Question 4: Longest trip for each day
**Task:** Which pickup day had the longest trip distance (trip_distance < 100 miles)?

**Answer: `2025-11-14`**

**SQL Query:**
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

**Result:** 2025-11-14 with 88.03 miles

---

## Question 5: Biggest pickup zone
**Task:** Which pickup zone had the largest total_amount on November 18th, 2025?

**Answer: `East Harlem North`**

**SQL Query:**
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

**Result:** East Harlem North with $9,281.92

---

## Question 6: Largest tip
**Task:** For pickups from "East Harlem North" in November 2025, which dropoff zone had the largest tip?

**Answer: `Yorkville West`**

**SQL Query:**
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

**Note:** Among the answer options provided:
- JFK Airport: $307.66
- Yorkville West: $2,403.17 ✓ (highest among options)
- East Harlem North: $604.10
- LaGuardia Airport: $1,835.52

---

## Question 7: Terraform Workflow
**Task:** Which sequence describes:
1. Downloading provider plugins and setting up backend
2. Generating proposed changes and auto-executing the plan
3. Remove all resources managed by terraform

**Answer: `terraform init, terraform apply -auto-approve, terraform destroy`**

**Explanation:**
1. `terraform init` - Downloads provider plugins and sets up backend
2. `terraform apply -auto-approve` - Generates plan and auto-executes it
3. `terraform destroy` - Removes all resources managed by Terraform

---

## Summary of All Answers

1. **Question 1:** Run `docker run --entrypoint bash python:3.13 -c "pip --version"` (requires Docker)
2. **Question 2:** `db:5432`
3. **Question 3:** `8,007`
4. **Question 4:** `2025-11-14`
5. **Question 5:** `East Harlem North`
6. **Question 6:** `Yorkville West`
7. **Question 7:** `terraform init, terraform apply -auto-approve, terraform destroy`
