-- MySQL schema for SensorLens — Sensor Data Analytics Platform

DROP TABLE IF EXISTS sensor_readings;
DROP TABLE IF EXISTS sensors;

CREATE TABLE sensors (
    sensor_id VARCHAR(20) PRIMARY KEY,
    first_seen DATETIME NOT NULL,
    last_seen DATETIME NOT NULL,
    reading_count INT NOT NULL,
    active_state_count INT NOT NULL
) ENGINE=InnoDB;

CREATE TABLE sensor_readings (
    reading_id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(20) NOT NULL,
    reading_ts DATETIME NOT NULL,
    state VARCHAR(20) NOT NULL,
    temperature DECIMAL(8,2) NOT NULL,
    humidity DECIMAL(8,2) NOT NULL,
    CONSTRAINT fk_sensor_readings_sensor FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id),
    CONSTRAINT ck_sensor_temp CHECK (temperature BETWEEN -20 AND 80),
    CONSTRAINT ck_sensor_humidity CHECK (humidity BETWEEN 0 AND 100)
) ENGINE=InnoDB;

CREATE INDEX idx_sensor_readings_sensor_ts ON sensor_readings(sensor_id, reading_ts);
CREATE INDEX idx_sensor_readings_ts ON sensor_readings(reading_ts);

