-- Optional MySQL schema for Settings → Advanced.
-- Default installs use SQLite in the chosen data folder. No passwords here.

CREATE DATABASE IF NOT EXISTS attendancedb DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE attendancedb;

CREATE TABLE IF NOT EXISTS people (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    external_id VARCHAR(64) NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'Staff',
    class_dept VARCHAR(128) NULL,
    photo_path VARCHAR(512) NULL,
    created_at VARCHAR(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS attended (
    id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT NULL,
    name VARCHAR(255) NOT NULL,
    time VARCHAR(16) NOT NULL,
    date VARCHAR(10) NOT NULL,
    UNIQUE KEY attended_person_date (person_id, date),
    CONSTRAINT fk_attended_person
        FOREIGN KEY (person_id) REFERENCES people(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
