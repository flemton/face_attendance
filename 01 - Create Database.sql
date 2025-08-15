CREATE DATABASE IF NOT EXISTS `attendancedb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `attendancedb`;

DROP TABLE IF EXISTS `attended`;
CREATE TABLE `attended` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `staff_id` INT,
  `name` VARCHAR(45),
  `time` VARCHAR(8),
  `date` DATE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `staff`;
CREATE TABLE `staff` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(45),
  `img_name` VARCHAR(45)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `staff` VALUES (1, 'Alhassan Osman', 'img/1.jpg'), (2, 'Sarkcess Alpha', 'img/2.jpg');
INSERT INTO `attended` VALUES (1, 1, 'Alhassan Osman', '05:44:10', '2021-11-06');