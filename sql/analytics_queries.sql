-- 1. Sensor ranking using a window function
SELECT sensor_id, reading_count,
       DENSE_RANK() OVER (ORDER BY reading_count DESC) usage_rank
FROM sensors ORDER BY usage_rank, sensor_id;

-- 2. Running count by sensor
SELECT sensor_id, reading_ts, reading_id,
       COUNT(*) OVER (PARTITION BY sensor_id ORDER BY reading_ts ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) running_readings
FROM sensor_readings;

-- 3. Previous reading comparison using LAG
SELECT sensor_id, reading_ts, temperature,
       LAG(temperature) OVER (PARTITION BY sensor_id ORDER BY reading_ts) previous_temperature,
       temperature - LAG(temperature) OVER (PARTITION BY sensor_id ORDER BY reading_ts) temperature_change
FROM sensor_readings;

-- 4. Sensor performance summary with HAVING
SELECT sensor_id, COUNT(*) readings, ROUND(AVG(temperature),2) avg_temperature
FROM sensor_readings GROUP BY sensor_id HAVING COUNT(*) >= 5 ORDER BY readings DESC;

-- 5. CTE for sensors above overall average activity
WITH sensor_counts AS (
    SELECT sensor_id, COUNT(*) reading_count FROM sensor_readings GROUP BY sensor_id
), overall_avg AS (
    SELECT AVG(reading_count) avg_count FROM sensor_counts
)
SELECT sc.sensor_id, sc.reading_count
FROM sensor_counts sc CROSS JOIN overall_avg oa
WHERE sc.reading_count > oa.avg_count ORDER BY sc.reading_count DESC;

-- 6. State distribution
SELECT state, COUNT(*) reading_count,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) pct_of_readings
FROM sensor_readings GROUP BY state ORDER BY reading_count DESC;

-- 7. Top sensors by active-state readings
SELECT sensor_id,
       SUM(CASE WHEN state IN ('ON','OPEN','PRESENT') THEN 1 ELSE 0 END) active_readings
FROM sensor_readings GROUP BY sensor_id ORDER BY active_readings DESC;

-- 8. Daily metrics
SELECT DATE(reading_ts) reading_date, COUNT(*) total_readings,
       ROUND(AVG(temperature),2) avg_temperature,
       ROUND(AVG(humidity),2) avg_humidity
FROM sensor_readings GROUP BY DATE(reading_ts) ORDER BY reading_date;

-- 9. Anomaly detection with CASE
SELECT reading_id, sensor_id, reading_ts, temperature, humidity,
       CASE WHEN temperature < 10 OR temperature > 35 THEN 'Temperature outlier'
            WHEN humidity < 30 OR humidity > 70 THEN 'Humidity outlier'
            ELSE 'Normal' END classification
FROM sensor_readings;

-- 10. Subquery: sensors with above-average temperature
SELECT sensor_id, ROUND(AVG(temperature),2) avg_temperature
FROM sensor_readings GROUP BY sensor_id
HAVING AVG(temperature) > (SELECT AVG(temperature) FROM sensor_readings)
ORDER BY avg_temperature DESC;
