CREATE OR REPLACE VIEW vw_sensor_summary AS
SELECT s.sensor_id, s.reading_count, s.first_seen, s.last_seen,
       ROUND(AVG(r.temperature),2) avg_temperature,
       ROUND(AVG(r.humidity),2) avg_humidity,
       SUM(CASE WHEN r.state IN ('ON','OPEN','PRESENT') THEN 1 ELSE 0 END) active_readings
FROM sensors s JOIN sensor_readings r ON r.sensor_id = s.sensor_id
GROUP BY s.sensor_id, s.reading_count, s.first_seen, s.last_seen;

CREATE OR REPLACE VIEW vw_daily_sensor_metrics AS
SELECT DATE(reading_ts) reading_date,
       COUNT(*) total_readings,
       COUNT(DISTINCT sensor_id) active_sensors,
       ROUND(AVG(temperature),2) avg_temperature,
       ROUND(AVG(humidity),2) avg_humidity,
       ROUND(MIN(temperature),2) min_temperature,
       ROUND(MAX(temperature),2) max_temperature
FROM sensor_readings
GROUP BY DATE(reading_ts);


CREATE OR REPLACE VIEW vw_anomalies AS
SELECT reading_id, sensor_id, reading_ts, state, temperature, humidity,
       CASE WHEN temperature < 10 OR temperature > 35 THEN 'TEMPERATURE_OUTLIER'
            WHEN humidity < 30 OR humidity > 70 THEN 'HUMIDITY_OUTLIER'
            ELSE 'NORMAL' END anomaly_type
FROM sensor_readings
WHERE temperature < 10 OR temperature > 35 OR humidity < 30 OR humidity > 70;
