------------------------------------------------new database--------------------------------------------------------------------------------------------------------
-- Urban Traffic Intelligence and Congestion Prediction System
-- Database Setup Script
-- Run this in MySQL: mysql -u root -p < database.sql

CREATE DATABASE IF NOT EXISTS urban_traffic_db;
USE urban_traffic_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Traffic Records Table
CREATE TABLE IF NOT EXISTS traffic_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    area VARCHAR(100) NOT NULL,
    road_name VARCHAR(150) NOT NULL,
    day VARCHAR(20) NOT NULL,
    time VARCHAR(20) NOT NULL,
    weather VARCHAR(50) NOT NULL,
    vehicle_count INT NOT NULL,
    average_speed FLOAT NOT NULL,
    road_type VARCHAR(50) NOT NULL,
    congestion_level ENUM('Low', 'Medium', 'High') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Prediction History Table
CREATE TABLE IF NOT EXISTS prediction_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    area VARCHAR(100) NOT NULL,
    road_name VARCHAR(150) NOT NULL,
    day VARCHAR(20) NOT NULL,
    time VARCHAR(20) NOT NULL,
    weather VARCHAR(50) NOT NULL,
    vehicle_count INT NOT NULL,
    average_speed FLOAT NOT NULL,
    road_type VARCHAR(50) NOT NULL,
    predicted_congestion ENUM('Low', 'Medium', 'High') NOT NULL,
    estimated_delay VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prediction_id INT,
    area VARCHAR(100) NOT NULL,
    road_name VARCHAR(150) NOT NULL,
    alert_message TEXT NOT NULL,
    congestion_level VARCHAR(20) NOT NULL,
    estimated_delay VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user (password: admin123)
INSERT IGNORE INTO users (name, email, password, role) VALUES
('Administrator', 'admin@traffic.com', 'pbkdf2:sha256:260000$admin123hash', 'admin'),
('Test User', 'user@traffic.com', 'pbkdf2:sha256:260000$user123hash', 'user');

-- Insert sample traffic records
INSERT INTO traffic_records (area, road_name, day, time, weather, vehicle_count, average_speed, road_type, congestion_level) VALUES
('Connaught Place', 'Rajpath Marg', 'Monday', '08:00 AM', 'Clear', 850, 25.5, 'Highway', 'High'),
('Bandra', 'Western Express Highway', 'Tuesday', '09:00 AM', 'Cloudy', 620, 35.0, 'Highway', 'Medium'),
('Electronic City', 'Hosur Road', 'Wednesday', '07:30 AM', 'Rainy', 920, 18.0, 'Urban Road', 'High'),
('Salt Lake', 'EM Bypass', 'Thursday', '06:00 PM', 'Clear', 410, 52.0, 'Expressway', 'Low'),
('Anna Nagar', 'Ring Road', 'Friday', '05:30 PM', 'Foggy', 780, 22.0, 'Urban Road', 'High'),
('Koramangala', 'Silk Board Junction', 'Monday', '09:30 AM', 'Clear', 950, 12.0, 'Urban Road', 'High'),
('Hitech City', 'HITEC City Road', 'Tuesday', '10:00 AM', 'Clear', 530, 45.0, 'Highway', 'Medium'),
('Dwarka', 'NH-48', 'Wednesday', '08:30 AM', 'Hazy', 670, 30.0, 'Highway', 'Medium'),
('Whitefield', 'Outer Ring Road', 'Thursday', '07:00 AM', 'Clear', 480, 55.0, 'Expressway', 'Low'),
('Powai', 'LBS Marg', 'Friday', '06:30 PM', 'Rainy', 830, 20.0, 'Urban Road', 'High');

USE urban_traffic_db;
INSERT INTO alerts 
(alert_message, area, congestion_level, estimated_delay, prediction_id, road_name, created_at)
VALUES
('High congestion detected. Avoid this route.', 'Market Road', 'High', 35, 1, 'Market Road', NOW()),
('Severe congestion alert. Use alternative road.', 'Sector A', 'High', 45, 1, 'Main Road', NOW()),
('Medium traffic alert. Slight delay expected.', 'Sector B', 'Medium', 18, 1, 'Expressway', NOW());

SHOW databases;

