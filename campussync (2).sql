-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Sep 27, 2026 at 12:49 PM
-- Server version: 8.4.7
-- PHP Version: 8.3.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `campussync`
--

-- --------------------------------------------------------

--
-- Table structure for table `academic_settings`
--

DROP TABLE IF EXISTS `academic_settings`;
CREATE TABLE IF NOT EXISTS `academic_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `academic_year` varchar(20) NOT NULL,
  `semester_cycle` enum('Odd','Even') NOT NULL,
  `cycle_start_date` date DEFAULT NULL,
  `cycle_end_date` date DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `students_per_division` int NOT NULL DEFAULT '70',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `academic_settings`
--

INSERT INTO `academic_settings` (`id`, `academic_year`, `semester_cycle`, `cycle_start_date`, `cycle_end_date`, `created_at`, `updated_at`, `students_per_division`) VALUES
(1, '2026-27', 'Odd', '2026-06-15', '2027-04-15', '2026-08-16 15:09:50', '2026-09-18 08:46:35', 70);

-- --------------------------------------------------------

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
CREATE TABLE IF NOT EXISTS `admins` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `profile_photo` varchar(255) DEFAULT 'default-avatar.png',
  `status` enum('Active','Inactive') DEFAULT 'Active',
  `last_login` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `reset_otp` varchar(255) DEFAULT NULL,
  `otp_expiry` datetime DEFAULT NULL,
  `otp_attempts` int NOT NULL DEFAULT '0',
  `otp_blocked_until` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`id`, `username`, `password`, `full_name`, `email`, `mobile`, `profile_photo`, `status`, `last_login`, `created_at`, `updated_at`, `reset_otp`, `otp_expiry`, `otp_attempts`, `otp_blocked_until`) VALUES
(1, 'admin', 'scrypt:32768:8:1$mTT8mRzZi5GbH4Bh$b7fd91d56951ce4c10437f20449dea9d1b0c0d75bf1fbe4c441069220da83a973178581a2bd779c228853114aacf6ef5cbf381be255ff6973fef8dec0a059458', 'Administrator', 'admin@campussync.com', '9876543210', 'admin_1_1787122477.jpeg', 'Active', '2026-09-24 07:27:46', '2026-08-02 08:55:04', '2026-09-24 01:57:46', NULL, NULL, 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `archived_internal_marks`
--

DROP TABLE IF EXISTS `archived_internal_marks`;
CREATE TABLE IF NOT EXISTS `archived_internal_marks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `enrollment_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `student_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subject_id` int DEFAULT NULL,
  `subject_code` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `subject_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `semester` smallint NOT NULL,
  `academic_year` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `marks_obtained` float NOT NULL,
  `max_marks` int NOT NULL,
  `component_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `archived_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_archived_internal_marks_enrollment_no` (`enrollment_no`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `archived_internal_marks`
--

INSERT INTO `archived_internal_marks` (`id`, `enrollment_no`, `student_name`, `subject_id`, `subject_code`, `subject_name`, `semester`, `academic_year`, `marks_obtained`, `max_marks`, `component_data`, `archived_at`) VALUES
(3, 'BCA15226000016', 'akash raval', 5, 'BCA501A', 'GUI Programming Using C# .net', 5, '2026-27', 45.15, 50, '{\"type\": \"Theory\", \"test1\": 12.0, \"test2\": 14.0, \"test3\": 7.0, \"best2\": 13.0, \"internal_exam\": 45.0, \"active_learning\": 5.0, \"class_assignment\": 5.0, \"home_assignment\": 5.0, \"attendance\": 3.75, \"total\": 45.15, \"max_marks\": 50.0}', '2026-09-18 08:29:20'),
(4, 'BCA15226000016', 'akash raval', 8, 'BCA501C', 'Practical - GUI Programming', 5, '2026-27', 22, 25, '{\"type\": \"Practical\", \"save_type\": \"final\", \"status\": \"final\", \"is_final\": true, \"internal_exam\": 9.0, \"practical_eval\": 9.0, \"viva\": null, \"journal\": 4.0, \"total\": 22.0, \"max_marks\": 25.0}', '2026-09-18 08:29:20'),
(5, 'BCA15226000020', 'DEVIDKUMAR DANABHAI PARMAR', 5, 'BCA501A', 'GUI Programming Using C# .net', 5, '2026-27', 45.88, 50, '{\"type\": \"Theory\", \"test1\": 13.0, \"test2\": 11.0, \"test3\": 9.0, \"best2\": 12.0, \"internal_exam\": 46.0, \"active_learning\": 5.0, \"class_assignment\": 5.0, \"home_assignment\": 5.0, \"attendance\": 5.0, \"total\": 45.88, \"max_marks\": 50.0}', '2026-09-18 08:29:20'),
(6, 'BCA15226000020', 'DEVIDKUMAR DANABHAI PARMAR', 8, 'BCA501C', 'Practical - GUI Programming', 5, '2026-27', 19, 25, '{\"type\": \"Practical\", \"save_type\": \"final\", \"status\": \"final\", \"is_final\": true, \"internal_exam\": 10.0, \"practical_eval\": 5.0, \"viva\": null, \"journal\": 4.0, \"total\": 19.0, \"max_marks\": 25.0}', '2026-09-18 08:29:20'),
(7, 'BCA15226000099', 'Rajesh Sharma (Alumni Test)', NULL, 'BCA501', 'Cloud Computing', 5, '2025-26', 42.5, 50, NULL, '2026-09-24 06:04:52'),
(8, 'BCA15226000099', 'Rajesh Sharma (Alumni Test)', NULL, 'BCA502', 'Web Frameworks', 5, '2025-26', 38, 50, NULL, '2026-09-24 06:04:52'),
(9, 'BCA15226000099', 'Rajesh Sharma (Alumni Test)', NULL, 'BCA601', 'Information Security', 6, '2025-26', 45, 50, NULL, '2026-09-24 06:04:52'),
(10, 'BCA15226000099', 'Rajesh Sharma (Alumni Test)', NULL, 'BCA602', 'Project Work & Viva', 6, '2025-26', 48, 50, NULL, '2026-09-24 06:04:52');

-- --------------------------------------------------------

--
-- Table structure for table `archived_students`
--

DROP TABLE IF EXISTS `archived_students`;
CREATE TABLE IF NOT EXISTS `archived_students` (
  `id` int NOT NULL AUTO_INCREMENT,
  `original_student_id` int DEFAULT NULL,
  `roll_number` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `enrollment_no` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `mobile` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `course` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `final_semester` smallint NOT NULL,
  `division` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `academic_year` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `profile_photo` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `archived_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_archived_students_enrollment_no` (`enrollment_no`)
) ENGINE=MyISAM AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `archived_students`
--

INSERT INTO `archived_students` (`id`, `original_student_id`, `roll_number`, `enrollment_no`, `full_name`, `email`, `mobile`, `dob`, `course`, `final_semester`, `division`, `academic_year`, `profile_photo`, `status`, `archived_at`) VALUES
(13, NULL, '99', 'BCA15226000099', 'Rajesh Sharma (Alumni Test)', 'test.alumni@college.edu', '9876543210', NULL, 'BCA', 6, 'A', '2025-26', 'default-avatar.png', 'Archived', '2026-09-24 06:04:52');

-- --------------------------------------------------------

--
-- Table structure for table `archived_student_otps`
--

DROP TABLE IF EXISTS `archived_student_otps`;
CREATE TABLE IF NOT EXISTS `archived_student_otps` (
  `id` int NOT NULL AUTO_INCREMENT,
  `enrollment_no` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `otp_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `expires_at` datetime NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `attempts` int NOT NULL DEFAULT '0',
  `blocked_until` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_archived_student_otps_enrollment_no` (`enrollment_no`)
) ENGINE=MyISAM AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `archived_student_otps`
--

INSERT INTO `archived_student_otps` (`id`, `enrollment_no`, `email`, `otp_hash`, `expires_at`, `is_verified`, `created_at`, `attempts`, `blocked_until`) VALUES
(3, 'BCA15226000016', 'akashraval3709@gmail.com', 'scrypt:32768:8:1$Z4clw5aRBf6ZFQxu$354de13e9a4c4fa1363c686407be872882d9e73f88496fff86656abb5c11c044835b33412060773b651a9f54c151664a02676d3c824127d0f38d74b5e9118a4d', '2026-09-24 08:56:05', 1, '2026-09-24 06:46:05', 0, '2026-09-24 17:12:53'),
(4, 'BCA15226000016', 'akashraval3709@gmail.com', 'scrypt:32768:8:1$y92SngvMefxKMxxN$a57b7bd8d55060a51833ee1b8b4e498410d7a361bc15ec2afbb207126509851e2d34bc09839319a089457e7b8d02ad863aa7d04bf0379f479746e31fb184f3b3', '2026-09-24 09:03:47', 1, '2026-09-24 06:53:47', 0, '2026-09-24 17:12:53'),
(13, 'BCA15226000020', 'devidparmar8954@gmail.com', 'scrypt:32768:8:1$66trC8XYokcF0Rn9$db013e8ff62c5efc60b78e2a1125bc52db87e072829555f56c766dfc68f7d0218e0d25c1637a332928a6fc9acd0323e31e60cf932582fe9b8cb2100efb94063d', '2026-09-24 09:15:04', 0, '2026-09-24 07:14:41', 0, '2026-09-24 17:15:47'),
(12, 'BCA15226000020', 'devidparmar8954@gmail.com', 'scrypt:32768:8:1$HpNmDOWeZmEavgX8$743d257d1dc0ad69e4704693af3b2b5fec2ca5c1cfab2ca1db8ac0404e46b657c0eb835fec8dd4fcdcddd8e9d8ec16b4003521a91a896594d8eac8b6181cc230', '2026-09-24 09:15:04', 0, '2026-09-24 07:14:03', 0, '2026-09-24 17:15:47'),
(11, 'BCA15226000016', 'akashraval3709@gmail.com', 'scrypt:32768:8:1$gbMD4GfTMPjMtIBl$a01b0ec96df224e39636ea7438d1a6fbfe22838f4dbc7f7b7a71359c7e73fde7859fa741a64c78d11f84feb4ddff2811ab1731ec9d72b1179cb4b9b92661ea68', '2026-09-24 09:22:06', 0, '2026-09-24 07:12:06', 0, '2026-09-24 17:12:53'),
(14, 'BCA15226000020', 'devidparmar8954@gmail.com', 'scrypt:32768:8:1$uX6dbIKrqGNLMuBT$de09315091f63299f80ebc2307c0f3a7b7df2f14989c19bf2d7c024d163cf66fb351ef4c1d6fc151fccefc07436143c9ad199ac379d9ce9ba5f0590e677ae279', '2026-09-24 09:25:04', 0, '2026-09-24 07:15:04', 0, '2026-09-24 17:15:47');

-- --------------------------------------------------------

--
-- Table structure for table `assignment_submissions`
--

DROP TABLE IF EXISTS `assignment_submissions`;
CREATE TABLE IF NOT EXISTS `assignment_submissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `notification_id` int NOT NULL,
  `student_id` int NOT NULL,
  `subject_id` int NOT NULL,
  `faculty_id` int DEFAULT NULL,
  `is_submitted` tinyint(1) NOT NULL,
  `submitted_at` datetime DEFAULT NULL,
  `marks_awarded` float DEFAULT NULL,
  `status` enum('Pending','Submitted','Late','Rejected') NOT NULL,
  `remarks` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_notification_student_submission` (`notification_id`,`student_id`),
  KEY `student_id` (`student_id`),
  KEY `subject_id` (`subject_id`),
  KEY `faculty_id` (`faculty_id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `assignment_submissions`
--

INSERT INTO `assignment_submissions` (`id`, `notification_id`, `student_id`, `subject_id`, `faculty_id`, `is_submitted`, `submitted_at`, `marks_awarded`, `status`, `remarks`, `created_at`, `updated_at`) VALUES
(7, 2, 127, 1, 1, 0, NULL, 0, 'Pending', NULL, '2026-09-26 02:04:18', '2026-09-26 02:04:18'),
(8, 2, 128, 1, 1, 0, NULL, 0, 'Pending', NULL, '2026-09-26 02:04:18', '2026-09-26 02:04:18'),
(9, 2, 129, 1, 1, 0, NULL, 0, 'Pending', NULL, '2026-09-26 02:04:18', '2026-09-26 02:04:18'),
(10, 2, 131, 1, 1, 0, NULL, 0, 'Pending', NULL, '2026-09-26 02:04:18', '2026-09-26 02:04:18'),
(11, 2, 134, 1, 1, 0, NULL, 0, 'Pending', NULL, '2026-09-26 02:04:18', '2026-09-26 02:04:18'),
(12, 2, 135, 1, 1, 0, NULL, 0, 'Pending', NULL, '2026-09-26 02:04:18', '2026-09-26 02:04:18'),
(13, 2, 138, 1, 1, 0, NULL, 0, 'Pending', NULL, '2026-09-26 02:04:18', '2026-09-26 02:04:18'),
(14, 2, 139, 1, 1, 0, NULL, 0, 'Pending', NULL, '2026-09-26 02:04:18', '2026-09-26 02:04:18');

-- --------------------------------------------------------

--
-- Table structure for table `attendance_records`
--

DROP TABLE IF EXISTS `attendance_records`;
CREATE TABLE IF NOT EXISTS `attendance_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `subject_id` int NOT NULL,
  `semester` smallint NOT NULL,
  `academic_year` varchar(20) NOT NULL,
  `division` varchar(10) NOT NULL,
  `total_lectures` int NOT NULL,
  `attended_lectures` int NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_student_attendance_sem_year` (`student_id`,`subject_id`,`semester`,`academic_year`),
  KEY `subject_id` (`subject_id`)
) ENGINE=MyISAM AUTO_INCREMENT=52 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `attendance_records`
--

INSERT INTO `attendance_records` (`id`, `student_id`, `subject_id`, `semester`, `academic_year`, `division`, `total_lectures`, `attended_lectures`, `created_at`, `updated_at`) VALUES
(25, 127, 1, 1, '2026-27', 'A', 40, 38, '2026-09-18 01:09:58', '2026-09-18 01:09:58'),
(10, 143, 5, 5, '2026-27', 'A', 4, 3, '2026-09-16 10:54:44', '2026-09-16 11:27:54'),
(11, 149, 5, 5, '2026-27', 'A', 4, 4, '2026-09-16 10:54:44', '2026-09-16 11:27:55'),
(12, 128, 1, 1, '2026-27', 'A', 1, 1, '2026-09-16 11:00:10', '2026-09-16 11:00:10'),
(13, 129, 1, 1, '2026-27', 'A', 1, 0, '2026-09-16 11:00:10', '2026-09-16 11:00:10'),
(14, 131, 1, 1, '2026-27', 'A', 1, 0, '2026-09-16 11:00:10', '2026-09-16 11:00:10'),
(15, 134, 1, 1, '2026-27', 'A', 1, 1, '2026-09-16 11:00:10', '2026-09-16 11:00:10'),
(16, 135, 1, 1, '2026-27', 'A', 1, 1, '2026-09-16 11:00:11', '2026-09-16 11:00:11'),
(17, 138, 1, 1, '2026-27', 'A', 1, 0, '2026-09-16 11:00:11', '2026-09-16 11:00:11'),
(18, 139, 1, 1, '2026-27', 'A', 1, 1, '2026-09-16 11:00:11', '2026-09-16 11:00:11'),
(19, 132, 1, 1, '2026-27', 'B', 1, 1, '2026-09-16 11:03:17', '2026-09-16 11:03:17'),
(20, 133, 1, 1, '2026-27', 'B', 1, 0, '2026-09-16 11:03:17', '2026-09-16 11:03:17'),
(21, 137, 1, 1, '2026-27', 'B', 1, 0, '2026-09-16 11:03:17', '2026-09-16 11:03:17'),
(22, 140, 1, 1, '2026-27', 'B', 1, 1, '2026-09-16 11:03:17', '2026-09-16 11:03:17'),
(23, 143, 6, 5, '2026-27', 'A', 4, 4, '2026-09-18 01:08:53', '2026-09-18 01:08:53'),
(24, 149, 6, 5, '2026-27', 'A', 4, 4, '2026-09-18 01:08:53', '2026-09-18 01:08:53'),
(26, 156, 5, 5, '2026-27', 'A', 6, 2, '2026-09-18 08:55:02', '2026-09-26 14:07:33'),
(27, 156, 8, 5, '2026-27', 'A', 1, 1, '2026-09-18 10:07:17', '2026-09-18 10:07:17'),
(28, 156, 7, 5, '2026-27', 'A', 1, 1, '2026-09-18 10:07:54', '2026-09-18 10:07:54'),
(34, 204, 6, 5, '2026-27', 'A', 9, 1, '2026-09-19 03:56:27', '2026-09-27 06:50:10'),
(35, 203, 6, 5, '2026-27', 'A', 9, 1, '2026-09-19 03:56:27', '2026-09-27 06:50:10'),
(33, 156, 6, 5, '2026-27', 'A', 9, 3, '2026-09-19 03:56:27', '2026-09-27 06:50:10'),
(36, 202, 6, 5, '2026-27', 'A', 9, 2, '2026-09-19 03:56:27', '2026-09-27 06:50:10'),
(37, 201, 6, 5, '2026-27', 'A', 9, 1, '2026-09-19 03:56:27', '2026-09-27 06:50:10'),
(38, 200, 6, 5, '2026-27', 'A', 9, 2, '2026-09-19 03:56:27', '2026-09-27 06:50:10'),
(39, 127, 1, 2, '2026-27', 'A', 0, 0, '2026-09-25 08:31:56', '2026-09-25 08:31:56'),
(40, 128, 1, 2, '2026-27', 'A', 0, 0, '2026-09-25 08:31:56', '2026-09-25 08:31:56'),
(41, 129, 1, 2, '2026-27', 'A', 0, 0, '2026-09-25 08:31:56', '2026-09-25 08:31:56'),
(42, 131, 1, 2, '2026-27', 'A', 0, 0, '2026-09-25 08:31:56', '2026-09-25 08:31:56'),
(43, 134, 1, 2, '2026-27', 'A', 0, 0, '2026-09-25 08:31:56', '2026-09-25 08:31:56'),
(44, 135, 1, 2, '2026-27', 'A', 0, 0, '2026-09-25 08:31:56', '2026-09-25 08:31:56'),
(45, 138, 1, 2, '2026-27', 'A', 0, 0, '2026-09-25 08:31:56', '2026-09-25 08:31:56'),
(46, 139, 1, 2, '2026-27', 'A', 0, 0, '2026-09-25 08:31:56', '2026-09-25 08:31:56'),
(47, 204, 5, 5, '2026-27', 'A', 6, 0, '2026-09-25 12:19:29', '2026-09-26 14:07:33'),
(48, 203, 5, 5, '2026-27', 'A', 6, 0, '2026-09-25 12:19:29', '2026-09-26 14:07:33'),
(49, 202, 5, 5, '2026-27', 'A', 6, 0, '2026-09-25 12:19:29', '2026-09-26 14:07:33'),
(50, 201, 5, 5, '2026-27', 'A', 6, 0, '2026-09-25 12:19:29', '2026-09-26 14:07:33'),
(51, 200, 5, 5, '2026-27', 'A', 6, 0, '2026-09-25 12:19:29', '2026-09-26 14:07:33');

-- --------------------------------------------------------

--
-- Table structure for table `attendance_security_alerts`
--

DROP TABLE IF EXISTS `attendance_security_alerts`;
CREATE TABLE IF NOT EXISTS `attendance_security_alerts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `student_id` int NOT NULL,
  `attempted_roll` varchar(20) DEFAULT NULL,
  `device_fingerprint` varchar(500) DEFAULT NULL,
  `conflicting_student_id` int DEFAULT NULL,
  `alert_type` enum('DUPLICATE_DEVICE','OUT_OF_GEOFENCE','EXPIRED_TOKEN','UNBOUND_DEVICE') NOT NULL,
  `alert_message` text,
  `scan_latitude` decimal(10,8) DEFAULT NULL,
  `scan_longitude` decimal(11,8) DEFAULT NULL,
  `distance_meters` float DEFAULT NULL,
  `faculty_action` enum('PENDING','APPROVED','REJECTED') DEFAULT 'PENDING',
  `resolved_by_faculty_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_session` (`session_id`),
  KEY `idx_student` (`student_id`),
  KEY `idx_alert_type` (`alert_type`)
) ENGINE=MyISAM AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `attendance_security_alerts`
--

INSERT INTO `attendance_security_alerts` (`id`, `session_id`, `student_id`, `attempted_roll`, `device_fingerprint`, `conflicting_student_id`, `alert_type`, `alert_message`, `scan_latitude`, `scan_longitude`, `distance_meters`, `faculty_action`, `resolved_by_faculty_id`, `created_at`, `updated_at`) VALUES
(1, 25, 127, '1', 'DEV-TEST-PHONE-1', NULL, 'OUT_OF_GEOFENCE', 'Student scanned from 127593m away (Allowed: 500m).', 23.02250000, 72.57140000, 127593, 'APPROVED', 6, '2026-09-25 08:31:56', '2026-09-25 08:31:56'),
(13, 30, 203, '4', 'HW-7AD44D3B-BDB2739B', NULL, 'UNBOUND_DEVICE', 'Attempted scan from unrecognized device #HW-7AD44 (Registered device: #HW-0B4FB).', NULL, NULL, NULL, 'REJECTED', 11, '2026-09-25 23:42:13', '2026-09-27 06:54:00'),
(3, 26, 201, '2', 'DEV-VM9L63RN-MUH6QKXB', NULL, 'OUT_OF_GEOFENCE', 'Student scanned from 700m away (Allowed: 500m).', 24.16216216, 72.39668186, 699.99, 'REJECTED', 11, '2026-09-25 11:12:52', '2026-09-25 11:27:46'),
(4, 26, 201, '2', 'DEV-VM9L63RN-MUH6QKXB', NULL, 'OUT_OF_GEOFENCE', 'Student scanned from 700m away (Allowed: 500m).', 24.16216216, 72.39668186, 699.99, 'REJECTED', 11, '2026-09-25 11:14:25', '2026-09-25 11:27:45'),
(5, 26, 200, '1', 'DEV-VM9L63RN-MUH6QKXB', 156, 'DUPLICATE_DEVICE', 'Device hash was already used by Roll 6 (Sachin Rathod). Potential proxy scan attempt.', NULL, NULL, NULL, 'APPROVED', 11, '2026-09-25 11:37:55', '2026-09-25 12:46:40'),
(6, 26, 200, '1', 'DEV-VM9L63RN-MUH6QKXB', 156, 'DUPLICATE_DEVICE', 'Device hash belongs to Roll 6 (Sachin Rathod). Potential proxy scan attempt.', 24.16216216, 72.39668186, NULL, 'REJECTED', 1, '2026-09-25 12:12:34', '2026-09-25 20:42:34'),
(7, 27, 201, '2', 'DEV-VM9L63RN-MUH6QKXB', 156, 'DUPLICATE_DEVICE', 'Device hash belongs to Roll 6 (Sachin Rathod). Potential proxy scan attempt.', 24.16216216, 72.39668186, NULL, 'REJECTED', 11, '2026-09-25 12:20:26', '2026-09-25 12:20:54'),
(8, 27, 200, '1', 'DEV-VM9L63RN-MUH6QKXB', 156, 'DUPLICATE_DEVICE', 'Device hash belongs to Roll 6 (Sachin Rathod). Potential proxy scan attempt.', 24.16216216, 72.39668186, NULL, 'APPROVED', 11, '2026-09-25 12:22:36', '2026-09-25 12:22:46'),
(9, 27, 201, '2', 'DEV-VM9L63RN-MUH6QKXB', 156, 'DUPLICATE_DEVICE', 'Device hash belongs to Roll 6 (Sachin Rathod). Potential proxy scan attempt.', 24.16216216, 72.39668186, NULL, 'REJECTED', 11, '2026-09-25 12:26:52', '2026-09-25 12:26:57'),
(14, 31, 156, '6', 'HW-7D85DE6D-59D78201', NULL, 'UNBOUND_DEVICE', 'Attempted scan from unrecognized device #HW-7D85D (Registered device: #HW-81774).', NULL, NULL, NULL, 'REJECTED', 11, '2026-09-26 13:03:34', '2026-09-26 13:04:46'),
(12, 29, 201, '2', 'DEV-URARHCM9-MUHA8SVC', 200, 'DUPLICATE_DEVICE', 'Device hash belongs to Roll 1 (Chirag Panchal). Potential proxy scan attempt.', 24.15951470, 72.40291590, NULL, 'REJECTED', 11, '2026-09-25 21:45:38', '2026-09-25 21:46:03'),
(16, 34, 200, '1', 'HW-220F9537-DC119916', NULL, 'UNBOUND_DEVICE', 'Attendance submitted from unrecognized/borrowed device #HW-220F9. Student requested faculty approval.', 24.15956990, 72.40294790, 3.64158, 'REJECTED', 11, '2026-09-27 04:01:22', '2026-09-27 06:27:06'),
(17, 36, 127, '1', 'TEST-DEV-123', NULL, 'OUT_OF_GEOFENCE', 'Student scanned from 135.32 km away (Maximum allowed: 800m).', 23.00000000, 72.00000000, 135316, 'PENDING', NULL, '2026-09-27 04:23:02', '2026-09-27 04:23:02'),
(18, 36, 127, '1', 'TEST-DEV-123', NULL, 'OUT_OF_GEOFENCE', 'Student scanned from 135.32 km away (Maximum allowed: 800m).', 23.00000000, 72.00000000, 135316, '', NULL, '2026-09-27 04:23:42', '2026-09-27 04:23:42'),
(19, 36, 127, '1', 'FRIEND-PHONE-FINGERPRINT', 128, 'DUPLICATE_DEVICE', 'Attendance submitted from friend\'s/alternate phone (Registered to Roll #2 - Aditya Vaghela). Student requested faculty approval.', 24.15953750, 72.40295313, 0, 'PENDING', NULL, '2026-09-27 04:23:42', '2026-09-27 04:23:42');

-- --------------------------------------------------------

--
-- Table structure for table `college_settings`
--

DROP TABLE IF EXISTS `college_settings`;
CREATE TABLE IF NOT EXISTS `college_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `college_name` varchar(255) NOT NULL,
  `college_short_name` varchar(50) DEFAULT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `address` text,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `pincode` varchar(10) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `website` varchar(255) DEFAULT NULL,
  `principal_name` varchar(100) DEFAULT NULL,
  `established_year` varchar(10) DEFAULT NULL,
  `description` text,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `college_type` varchar(50) DEFAULT 'BCA',
  `college_stamp` varchar(255) DEFAULT 'default-stamp.png',
  `principal_signature` varchar(255) DEFAULT 'default-signature.png',
  `min_overall_attendance` float NOT NULL DEFAULT '75',
  `min_subject_attendance` float NOT NULL DEFAULT '75',
  `attendance_warning_threshold` float NOT NULL DEFAULT '60',
  `campus_latitude` decimal(10,8) DEFAULT '23.83680000',
  `campus_longitude` decimal(11,8) DEFAULT '72.11240000',
  `campus_radius_meters` int DEFAULT '150',
  `campus_plus_code` varchar(100) DEFAULT '5C53+R58 Palanpur, Gujarat',
  `college_start_time` varchar(10) DEFAULT '10:00',
  `college_end_time` varchar(10) DEFAULT '17:00',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `college_settings`
--

INSERT INTO `college_settings` (`id`, `college_name`, `college_short_name`, `logo`, `address`, `city`, `state`, `pincode`, `phone`, `email`, `website`, `principal_name`, `established_year`, `description`, `created_at`, `updated_at`, `college_type`, `college_stamp`, `principal_signature`, `min_overall_attendance`, `min_subject_attendance`, `attendance_warning_threshold`, `campus_latitude`, `campus_longitude`, `campus_radius_meters`, `campus_plus_code`, `college_start_time`, `college_end_time`) VALUES
(1, 'CampusSync College', '', 'college_logo_1787122488.png', '', '', '', '', '', '', '', '', '', '', '2026-08-12 06:46:37', '2026-09-25 11:20:18', '', 'college_stamp_1789729887.png', 'principal_sig_1789729887.png', 70, 70, 50, 24.15953750, 72.40295313, 800, '5C53+R58 Palanpur, Gujarat', '10:00', '17:00');

-- --------------------------------------------------------

--
-- Table structure for table `email_logs`
--

DROP TABLE IF EXISTS `email_logs`;
CREATE TABLE IF NOT EXISTS `email_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `email_type` varchar(50) NOT NULL,
  `recipient_email` varchar(100) NOT NULL,
  `status` enum('PENDING','SENDING','SENT','FAILED') NOT NULL,
  `error_message` text,
  `sent_at` datetime DEFAULT NULL,
  `retry_count` int NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`)
) ENGINE=MyISAM AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `email_logs`
--

INSERT INTO `email_logs` (`id`, `student_id`, `email_type`, `recipient_email`, `status`, `error_message`, `sent_at`, `retry_count`, `created_at`, `updated_at`) VALUES
(1, 143, 'WELCOME', 'akashraval3709@gmail.com', 'SENT', NULL, '2026-09-13 15:23:50', 0, '2026-09-13 09:53:27', '2026-09-13 09:53:50'),
(2, 144, 'WELCOME', 'piyush@gmail.com', 'SENT', NULL, '2026-09-14 03:15:03', 0, '2026-09-13 21:44:43', '2026-09-13 21:45:03'),
(3, 145, 'WELCOME', 'nandni.devloper17@gmail.com', 'SENT', NULL, '2026-09-18 11:16:24', 1, '2026-09-14 04:09:17', '2026-09-18 05:46:24'),
(4, 146, 'WELCOME', 'nandni@gmail.com', 'SENT', NULL, '2026-09-18 11:16:20', 1, '2026-09-14 04:21:10', '2026-09-18 05:46:20'),
(5, 149, 'WELCOME', 'devidparmar8954@gmail.com', 'SENT', NULL, '2026-09-18 11:16:19', 1, '2026-09-16 08:05:36', '2026-09-18 05:46:19'),
(12, 156, 'WELCOME', 'sachin123@gmail.com', 'SENT', NULL, '2026-09-18 13:53:25', 0, '2026-09-18 08:23:03', '2026-09-18 08:23:25'),
(46, 205, 'WELCOME', 'akash@gmail.com', 'SENT', NULL, '2026-09-26 18:40:37', 0, '2026-09-26 13:10:17', '2026-09-26 13:10:37');

-- --------------------------------------------------------

--
-- Table structure for table `faculty`
--

DROP TABLE IF EXISTS `faculty`;
CREATE TABLE IF NOT EXISTS `faculty` (
  `id` int NOT NULL AUTO_INCREMENT,
  `faculty_code` varchar(50) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `mobile` varchar(15) NOT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `qualification` varchar(150) DEFAULT NULL,
  `designation` varchar(100) DEFAULT NULL,
  `department` varchar(50) DEFAULT NULL,
  `joining_date` date DEFAULT NULL,
  `address` text,
  `city` varchar(100) DEFAULT NULL,
  `state` varchar(100) DEFAULT NULL,
  `pincode` varchar(10) DEFAULT NULL,
  `profile_photo` varchar(255) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `password_changed` tinyint(1) NOT NULL,
  `status` enum('Active','Inactive') NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `reset_otp` varchar(255) DEFAULT NULL,
  `otp_expiry` datetime DEFAULT NULL,
  `otp_attempts` int NOT NULL DEFAULT '0',
  `otp_blocked_until` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `faculty_code` (`faculty_code`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `faculty`
--

INSERT INTO `faculty` (`id`, `faculty_code`, `full_name`, `email`, `mobile`, `gender`, `dob`, `qualification`, `designation`, `department`, `joining_date`, `address`, `city`, `state`, `pincode`, `profile_photo`, `password`, `password_changed`, `status`, `last_login`, `created_at`, `updated_at`, `reset_otp`, `otp_expiry`, `otp_attempts`, `otp_blocked_until`) VALUES
(6, 'FAC001', 'DEVIDKUMAR DANABHAI PARMAR', 'devidparmar8954@gmail.com', '9054702563', 'Male', NULL, 'MCA', 'Assistant Professor', 'BCA', NULL, '', '', '', '', 'faculty_FAC001_1789164034.jpg', 'scrypt:32768:8:1$nyIqavhoWSPF9avd$97d151e803921e66b06b279e60ce0dfbe288d32d2a7120fb0bf575fd7767d8d341746adcaca7429c3ca330a1a25759ca7fb376371de65b19812e10b2b7301181', 1, 'Active', '2026-09-12 04:16:39', '2026-09-11 22:00:35', '2026-09-18 01:30:27', NULL, NULL, 0, NULL),
(11, 'FAC002', 'RAVAL AKASHBHAI RAMESHBHAI', 'ar3897903@gmail.com', '9328976260', 'Male', NULL, 'MCA', 'Assistant Professor', 'BCA', NULL, '', '', '', '', 'faculty_FAC002_1789168745.jpg', 'scrypt:32768:8:1$zHq6kdNLmJIisgkB$4ef77e4f00ce2b9cc68ad035c158fad9f1bb967344c283d81621f933015008aae4a15ca3644b8e8d6b77c9c8e379c052e7656262e7949d1bc202fd4e6feccf57', 1, 'Active', '2026-09-27 12:22:35', '2026-09-11 23:19:06', '2026-09-27 06:52:35', 'scrypt:32768:8:1$QhKAzaUxglAg1EYE$eb8f17cc047e559ad83252dd07c2b9a24193840da42c4ed5573a283f339df7d76eeba5290adba4ada0e0db7c7e9d25743fa996d56994f018d7882206d7ef9a4f', '2026-09-24 09:12:53', 3, '2026-09-24 17:02:53'),
(12, 'FAC003', 'piyush', 'piyush@gmail.com', '9904089637', 'Male', '2011-03-16', 'MCA', 'Assistant Professor', 'BCA', '2026-09-18', '', '', '', '', 'default-avatar.png', 'scrypt:32768:8:1$z7cxzZFiBSplKKWa$0a6081eb242da9ba9c2b1d1757962fd4c7c784ae3c32b1b7407d4f9dfef2daf972c8540a2d54a3da99bc15921ec36fbbe0d351415996ce819ea7d741c961b5ab', 1, 'Active', '2026-09-18 17:13:23', '2026-09-18 00:22:34', '2026-09-18 11:43:23', NULL, NULL, 0, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `faculty_subject_assignments`
--

DROP TABLE IF EXISTS `faculty_subject_assignments`;
CREATE TABLE IF NOT EXISTS `faculty_subject_assignments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `faculty_id` int NOT NULL,
  `subject_id` int NOT NULL,
  `division` varchar(10) NOT NULL,
  `status` enum('Active','Inactive') NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_faculty_subject_division` (`faculty_id`,`subject_id`,`division`),
  KEY `subject_id` (`subject_id`)
) ENGINE=MyISAM AUTO_INCREMENT=155 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `faculty_subject_assignments`
--

INSERT INTO `faculty_subject_assignments` (`id`, `faculty_id`, `subject_id`, `division`, `status`, `created_at`, `updated_at`) VALUES
(143, 6, 1, 'A', 'Active', '2026-09-18 11:37:23', '2026-09-18 11:37:23'),
(154, 11, 8, 'A', 'Active', '2026-09-25 12:17:43', '2026-09-25 12:17:43'),
(153, 11, 5, 'A', 'Active', '2026-09-25 12:17:43', '2026-09-25 12:17:43'),
(152, 11, 7, 'A', 'Active', '2026-09-25 12:17:43', '2026-09-25 12:17:43'),
(151, 11, 6, 'B', 'Active', '2026-09-25 12:17:43', '2026-09-25 12:17:43'),
(150, 11, 6, 'A', 'Active', '2026-09-25 12:17:43', '2026-09-25 12:17:43'),
(136, 12, 1, 'B', 'Active', '2026-09-18 11:36:57', '2026-09-18 11:36:57'),
(137, 12, 2, 'A', 'Active', '2026-09-18 11:36:57', '2026-09-18 11:36:57'),
(138, 12, 2, 'B', 'Active', '2026-09-18 11:36:57', '2026-09-18 11:36:57'),
(139, 12, 2, 'C', 'Active', '2026-09-18 11:36:57', '2026-09-18 11:36:57'),
(140, 12, 10, 'A', 'Active', '2026-09-18 11:36:57', '2026-09-18 11:36:57'),
(141, 12, 10, 'B', 'Active', '2026-09-18 11:36:57', '2026-09-18 11:36:57'),
(142, 12, 10, 'C', 'Active', '2026-09-18 11:36:57', '2026-09-18 11:36:57'),
(144, 6, 3, 'A', 'Active', '2026-09-18 11:37:23', '2026-09-18 11:37:23'),
(145, 6, 3, 'B', 'Active', '2026-09-18 11:37:23', '2026-09-18 11:37:23'),
(146, 6, 3, 'C', 'Active', '2026-09-18 11:37:23', '2026-09-18 11:37:23'),
(147, 6, 28, 'A', 'Active', '2026-09-18 11:37:23', '2026-09-18 11:37:23'),
(148, 6, 28, 'B', 'Active', '2026-09-18 11:37:23', '2026-09-18 11:37:23'),
(149, 6, 28, 'C', 'Active', '2026-09-18 11:37:23', '2026-09-18 11:37:23');

-- --------------------------------------------------------

--
-- Table structure for table `gallery_items`
--

DROP TABLE IF EXISTS `gallery_items`;
CREATE TABLE IF NOT EXISTS `gallery_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(150) NOT NULL,
  `category` varchar(50) NOT NULL,
  `description` text,
  `image_file` varchar(255) NOT NULL,
  `is_featured` tinyint(1) NOT NULL,
  `status` enum('Active','Inactive') NOT NULL,
  `uploaded_by_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `views_count` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `uploaded_by_id` (`uploaded_by_id`)
) ENGINE=MyISAM AUTO_INCREMENT=89 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `gallery_items`
--

INSERT INTO `gallery_items` (`id`, `title`, `category`, `description`, `image_file`, `is_featured`, `status`, `uploaded_by_id`, `created_at`, `updated_at`, `views_count`) VALUES
(1, 'akash raval', 'Celebrations', NULL, 'gallery_20260926_150625_adc8fee8.jpeg', 1, 'Active', 1, '2026-09-26 04:06:26', '2026-09-27 02:13:34', 2),
(2, 'David', 'Celebrations', NULL, 'gallery_20260926_150925_10988d6b.jpg', 1, 'Active', 1, '2026-09-26 04:09:26', '2026-09-26 04:18:09', 0),
(3, 'Modern Central Library & Study Wing', 'Campus Life', 'Quiet air-conditioned digital library with thousands of reference books, e-journals, and peaceful study pods.', 'gallery_seed_campus_life_1.jpg', 1, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:26:02', 84),
(4, 'Green Smart Campus Walkway & Gardens', 'Campus Life', 'Eco-friendly landscaped gardens, tree-lined walking tracks, and open-air seating for students between lectures.', 'gallery_seed_campus_life_2.jpg', 0, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:39:14', 53),
(5, 'Advanced Computer & AI Research Lab', 'Campus Life', 'High-performance computing systems, dual-monitor programming workstations, and high-speed campus WiFi network.', 'gallery_seed_campus_life_3.jpg', 0, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:39:17', 68),
(6, 'Annual Cultural Fest & Live Concert', 'Events & Fests', 'High-energy musical concert night featuring celebrity artists, laser show lights, and enthusiastic crowd.', 'gallery_seed_events_fests_1.jpg', 1, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:26:02', 142),
(7, 'Campus Youth Hackathon 2026', 'Events & Fests', '24-hour inter-college coding marathon where teams built innovative web, mobile, and AI solutions overnight.', 'gallery_seed_events_fests_2.jpg', 0, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:39:17', 97),
(8, 'TechFusion Robotics & Project Expo', 'Events & Fests', 'Annual state-level technical exhibition showcasing student-built robotics, IoT automation, and drone demonstrations.', 'gallery_seed_events_fests_3.jpg', 0, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:39:17', 79),
(9, 'Inter-College Cricket Tournament', 'Sports', 'Thrilling championship cricket match under lights at the university sports complex with loud student cheers.', 'gallery_seed_sports_1.jpg', 1, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:26:02', 115),
(10, 'Annual Football Championship Finals', 'Sports', 'Exciting final clash of the inter-department football tournament on the main green athletic turf.', 'gallery_seed_sports_2.svg', 0, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:39:17', 90),
(88, 'Campus Basketball League & Athletics Meet', 'Sports', 'High-paced basketball finals and track races showcasing outstanding student athleticism and team spirit.', 'gallery_seed_sports_3.jpg', 0, 'Active', NULL, '2026-09-26 04:43:12', '2026-09-26 04:43:12', 64),
(12, 'International Seminar on AI & Machine Learning', 'Academic & Seminars', 'Keynote address by leading global industry experts on generative AI trends in the campus auditorium.', 'gallery_seed_academic_1.jpg', 1, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:26:02', 103),
(13, 'Interactive Faculty Workshop & Hands-on Coding', 'Academic & Seminars', 'Intensive skill-building workshop where students collaborated closely with mentors on cloud architecture.', 'gallery_seed_academic_2.jpg', 0, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:26:02', 71),
(14, 'Science Innovation & Research Symposium', 'Academic & Seminars', 'Young researchers and undergraduate students demonstrating working hardware models and research papers.', 'gallery_seed_academic_3.jpg', 0, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:26:02', 59),
(16, 'State Championship Trophy Award', 'Achievements', 'Campus team proudly lifting the overall championship trophy at the state inter-university athletic meet.', 'gallery_seed_achievements_2.jpg', 0, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:26:02', 112),
(17, 'National Hackathon Gold Medalist Felicitation', 'Achievements', 'College felicitation ceremony honoring the 1st prize winners of the Smart India Hackathon with cash prize and medals.', 'gallery_seed_achievements_3.svg', 0, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:35:54', 95),
(18, 'Campus Traditional Day & Garba Mahotsav', 'Celebrations', 'Joyous celebration of cultural heritage with vibrant ethnic attires, traditional music, and campus-wide unity.', 'gallery_seed_celebrations_3.jpg', 1, 'Active', NULL, '2026-09-26 04:26:02', '2026-09-26 04:26:02', 135);

-- --------------------------------------------------------

--
-- Table structure for table `home_page_settings`
--

DROP TABLE IF EXISTS `home_page_settings`;
CREATE TABLE IF NOT EXISTS `home_page_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `hero_headline` varchar(255) NOT NULL,
  `hero_subtitle` text NOT NULL,
  `hero_pill_badge` varchar(120) NOT NULL,
  `hero_banner_image` varchar(255) DEFAULT NULL,
  `hero_cta1_text` varchar(60) NOT NULL,
  `hero_cta1_link` varchar(255) NOT NULL,
  `hero_cta2_text` varchar(60) NOT NULL,
  `hero_cta2_link` varchar(255) NOT NULL,
  `stat1_number` varchar(50) NOT NULL,
  `stat1_label` varchar(100) NOT NULL,
  `stat1_active` tinyint(1) NOT NULL,
  `stat2_number` varchar(50) NOT NULL,
  `stat2_label` varchar(100) NOT NULL,
  `stat2_active` tinyint(1) NOT NULL,
  `stat3_number` varchar(50) NOT NULL,
  `stat3_label` varchar(100) NOT NULL,
  `stat3_active` tinyint(1) NOT NULL,
  `stat4_number` varchar(50) NOT NULL,
  `stat4_label` varchar(100) NOT NULL,
  `stat4_active` tinyint(1) NOT NULL,
  `ticker_active` tinyint(1) NOT NULL,
  `ticker_badge` varchar(50) NOT NULL,
  `ticker_text` text NOT NULL,
  `feat1_title` varchar(100) NOT NULL,
  `feat1_desc` text NOT NULL,
  `feat2_title` varchar(100) NOT NULL,
  `feat2_desc` text NOT NULL,
  `feat3_title` varchar(100) NOT NULL,
  `feat3_desc` text NOT NULL,
  `feat4_title` varchar(100) NOT NULL,
  `feat4_desc` text NOT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `home_page_settings`
--

INSERT INTO `home_page_settings` (`id`, `hero_headline`, `hero_subtitle`, `hero_pill_badge`, `hero_banner_image`, `hero_cta1_text`, `hero_cta1_link`, `hero_cta2_text`, `hero_cta2_link`, `stat1_number`, `stat1_label`, `stat1_active`, `stat2_number`, `stat2_label`, `stat2_active`, `stat3_number`, `stat3_label`, `stat3_active`, `stat4_number`, `stat4_label`, `stat4_active`, `ticker_active`, `ticker_badge`, `ticker_text`, `feat1_title`, `feat1_desc`, `feat2_title`, `feat2_desc`, `feat3_title`, `feat3_desc`, `feat4_title`, `feat4_desc`, `updated_at`) VALUES
(1, 'CampusSync Digital ERP', 'A unified platform to streamline QR attendance, exam results, faculty registers, and campus announcements — all in one place.', '✨ Smart QR Attendance System', NULL, 'Access Portals', '#portals', 'Explore Features', '#features', '5,000+', 'Enrolled Students', 1, '150+', 'Faculty Members', 1, '99.8%', 'Attendance Accuracy', 1, '100%', 'Placement Assistance', 1, 1, 'LATEST', 'Admissions open for Academic Year 2026-27. Submit applications online via student portal.', 'QR Attendance', 'Faculty generates dynamic QR to prevent proxy attendance.', 'Grade Entry', 'Streamlined internal mark submission and grading tables.', 'Web Management', 'Admin manages banners, galleries, and public notices easily.', 'Yearly Reports', 'Visual yearly analytics on attendance and pass rates.', '2026-09-26 05:06:56');

-- --------------------------------------------------------

--
-- Table structure for table `internal_marks`
--

DROP TABLE IF EXISTS `internal_marks`;
CREATE TABLE IF NOT EXISTS `internal_marks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `enrollment_no` varchar(20) DEFAULT NULL,
  `subject_id` int NOT NULL,
  `semester` smallint NOT NULL,
  `academic_year` varchar(20) NOT NULL,
  `marks_obtained` float NOT NULL,
  `max_marks` int NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `test1` float DEFAULT NULL,
  `test2` float DEFAULT NULL,
  `test3` float DEFAULT NULL,
  `internal_exam` float DEFAULT NULL,
  `quiz1` float DEFAULT NULL,
  `quiz2` float DEFAULT NULL,
  `quiz3` float DEFAULT NULL,
  `quiz4` float DEFAULT NULL,
  `active_learning` float DEFAULT NULL,
  `class_assignment` float DEFAULT NULL,
  `home_assignment` float DEFAULT NULL,
  `attendance` float DEFAULT NULL,
  `practical_eval` float DEFAULT NULL,
  `viva` float DEFAULT NULL,
  `journal` float DEFAULT NULL,
  `component_data` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_student_internal_mark_sem_year` (`student_id`,`subject_id`,`semester`,`academic_year`),
  KEY `subject_id` (`subject_id`),
  KEY `idx_internal_marks_enrollment` (`enrollment_no`)
) ENGINE=MyISAM AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `internal_marks`
--

INSERT INTO `internal_marks` (`id`, `student_id`, `enrollment_no`, `subject_id`, `semester`, `academic_year`, `marks_obtained`, `max_marks`, `created_at`, `updated_at`, `test1`, `test2`, `test3`, `internal_exam`, `quiz1`, `quiz2`, `quiz3`, `quiz4`, `active_learning`, `class_assignment`, `home_assignment`, `attendance`, `practical_eval`, `viva`, `journal`, `component_data`) VALUES
(15, 127, 'BCA15226000001', 1, 1, '2026-27', 23.33, 50, '2026-09-13 22:08:44', '2026-09-18 01:30:42', 12, 14, 10, 13, 0, 0, 0, 0, 4, 4, 4, 4, NULL, NULL, NULL, '{\"type\": \"Theory\", \"save_type\": \"draft\", \"status\": \"draft\", \"is_final\": false, \"test1\": 12.0, \"test2\": 14.0, \"test3\": 10.0, \"best2\": 13.0, \"internal_exam\": 13.0, \"active_learning\": 4.0, \"class_assignment\": 4.0, \"home_assignment\": 4.0, \"attendance\": 4.0, \"total\": 23.33, \"max_marks\": 50.0}'),
(21, 127, 'BCA15226000001', 2, 1, '2026-27', 21, 25, '2026-09-17 21:19:46', '2026-09-17 23:02:57', NULL, NULL, NULL, 8, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 9, 0, 4, '{\"type\": \"Practical\", \"save_type\": \"draft\", \"status\": \"draft\", \"is_final\": false, \"internal_exam\": 8.0, \"practical_eval\": 9.0, \"viva\": 0.0, \"journal\": 4.0, \"total\": 21.0, \"max_marks\": 25.0}'),
(7, 144, 'BCA15226000017', 3, 4, '2026-27', 49.67, 50, '2026-09-13 21:49:59', '2026-09-13 21:49:59', 15, 15, 15, NULL, 15, 15, 14, 10, 5, 5, 5, 5, NULL, NULL, NULL, '{\"type\": \"Theory\", \"test1\": 15.0, \"test2\": 15.0, \"test3\": 15.0, \"quiz1\": 15.0, \"quiz2\": 15.0, \"quiz3\": 14.0, \"quiz4\": 10.0, \"active_learning\": 5.0, \"class_assignment\": 5.0, \"home_assignment\": 5.0, \"attendance\": 5.0, \"class_test_calculated\": 15.0, \"quiz_calculated\": 14.67, \"total\": 49.67}'),
(16, 127, 'BCA15226000001', 1, 2, '2026-27', 25, 50, '2026-09-13 22:08:44', '2026-09-13 22:08:44', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(8, 138, 'BCA15226000012', 1, 1, '2026-27', 11, 50, '2026-09-13 22:07:41', '2026-09-13 23:37:36', 10, 12, 0, NULL, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, NULL, NULL, '{\"type\": \"Theory\", \"test1\": 10.0, \"test2\": 12.0, \"test3\": 0.0, \"quiz1\": 0.0, \"quiz2\": 0.0, \"quiz3\": 0.0, \"quiz4\": 0.0, \"active_learning\": 0.0, \"class_assignment\": 0.0, \"home_assignment\": 0.0, \"attendance\": 0.0, \"class_test_calculated\": 11.0, \"quiz_calculated\": 0.0, \"raw_total_50\": 11.0, \"total\": 11.0}'),
(9, 139, 'BCA15226000013', 1, 1, '2026-27', 11, 50, '2026-09-13 22:07:41', '2026-09-13 23:37:36', 10, 12, 0, NULL, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, NULL, NULL, '{\"type\": \"Theory\", \"test1\": 10.0, \"test2\": 12.0, \"test3\": 0.0, \"quiz1\": 0.0, \"quiz2\": 0.0, \"quiz3\": 0.0, \"quiz4\": 0.0, \"active_learning\": 0.0, \"class_assignment\": 0.0, \"home_assignment\": 0.0, \"attendance\": 0.0, \"class_test_calculated\": 11.0, \"quiz_calculated\": 0.0, \"raw_total_50\": 11.0, \"total\": 11.0}'),
(10, 128, 'BCA15226000002', 1, 1, '2026-27', 11, 50, '2026-09-13 22:07:41', '2026-09-13 23:37:36', 10, 12, 0, NULL, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, NULL, NULL, '{\"type\": \"Theory\", \"test1\": 10.0, \"test2\": 12.0, \"test3\": 0.0, \"quiz1\": 0.0, \"quiz2\": 0.0, \"quiz3\": 0.0, \"quiz4\": 0.0, \"active_learning\": 0.0, \"class_assignment\": 0.0, \"home_assignment\": 0.0, \"attendance\": 0.0, \"class_test_calculated\": 11.0, \"quiz_calculated\": 0.0, \"raw_total_50\": 11.0, \"total\": 11.0}'),
(11, 129, 'BCA15226000003', 1, 1, '2026-27', 11, 50, '2026-09-13 22:07:41', '2026-09-13 23:37:36', 10, 12, 0, NULL, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, NULL, NULL, '{\"type\": \"Theory\", \"test1\": 10.0, \"test2\": 12.0, \"test3\": 0.0, \"quiz1\": 0.0, \"quiz2\": 0.0, \"quiz3\": 0.0, \"quiz4\": 0.0, \"active_learning\": 0.0, \"class_assignment\": 0.0, \"home_assignment\": 0.0, \"attendance\": 0.0, \"class_test_calculated\": 11.0, \"quiz_calculated\": 0.0, \"raw_total_50\": 11.0, \"total\": 11.0}'),
(12, 131, 'BCA15226000005', 1, 1, '2026-27', 11, 50, '2026-09-13 22:07:41', '2026-09-13 23:37:36', 10, 12, 0, NULL, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, NULL, NULL, '{\"type\": \"Theory\", \"test1\": 10.0, \"test2\": 12.0, \"test3\": 0.0, \"quiz1\": 0.0, \"quiz2\": 0.0, \"quiz3\": 0.0, \"quiz4\": 0.0, \"active_learning\": 0.0, \"class_assignment\": 0.0, \"home_assignment\": 0.0, \"attendance\": 0.0, \"class_test_calculated\": 11.0, \"quiz_calculated\": 0.0, \"raw_total_50\": 11.0, \"total\": 11.0}'),
(13, 134, 'BCA15226000008', 1, 1, '2026-27', 11, 50, '2026-09-13 22:07:41', '2026-09-13 23:37:36', 10, 12, 0, NULL, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, NULL, NULL, '{\"type\": \"Theory\", \"test1\": 10.0, \"test2\": 12.0, \"test3\": 0.0, \"quiz1\": 0.0, \"quiz2\": 0.0, \"quiz3\": 0.0, \"quiz4\": 0.0, \"active_learning\": 0.0, \"class_assignment\": 0.0, \"home_assignment\": 0.0, \"attendance\": 0.0, \"class_test_calculated\": 11.0, \"quiz_calculated\": 0.0, \"raw_total_50\": 11.0, \"total\": 11.0}'),
(14, 135, 'BCA15226000009', 1, 1, '2026-27', 11, 50, '2026-09-13 22:07:41', '2026-09-13 23:37:36', 10, 12, 0, NULL, 0, 0, 0, 0, 0, 0, 0, NULL, NULL, NULL, NULL, '{\"type\": \"Theory\", \"test1\": 10.0, \"test2\": 12.0, \"test3\": 0.0, \"quiz1\": 0.0, \"quiz2\": 0.0, \"quiz3\": 0.0, \"quiz4\": 0.0, \"active_learning\": 0.0, \"class_assignment\": 0.0, \"home_assignment\": 0.0, \"attendance\": 0.0, \"class_test_calculated\": 11.0, \"quiz_calculated\": 0.0, \"raw_total_50\": 11.0, \"total\": 11.0}'),
(19, 143, 'BCA15226000016', 5, 5, '2026-27', 45.15, 50, '2026-09-16 08:17:44', '2026-09-17 21:39:49', 12, 14, 7, 45, 8, 5, 7, 4, 5, 5, 5, 3.75, NULL, NULL, NULL, '{\"type\": \"Theory\", \"test1\": 12.0, \"test2\": 14.0, \"test3\": 7.0, \"best2\": 13.0, \"internal_exam\": 45.0, \"active_learning\": 5.0, \"class_assignment\": 5.0, \"home_assignment\": 5.0, \"attendance\": 3.75, \"total\": 45.15, \"max_marks\": 50.0}'),
(20, 149, 'BCA15226000020', 5, 5, '2026-27', 45.88, 50, '2026-09-16 08:17:44', '2026-09-17 21:39:49', 13, 11, 9, 46, 4, 5, 7, 6, 5, 5, 5, 5, NULL, NULL, NULL, '{\"type\": \"Theory\", \"test1\": 13.0, \"test2\": 11.0, \"test3\": 9.0, \"best2\": 12.0, \"internal_exam\": 46.0, \"active_learning\": 5.0, \"class_assignment\": 5.0, \"home_assignment\": 5.0, \"attendance\": 5.0, \"total\": 45.88, \"max_marks\": 50.0}'),
(22, 127, 'BCA15226000001', 6, 5, '2026-27', 43, 50, '2026-09-17 23:00:10', '2026-09-17 23:00:10', 10, 12, 14, 14, NULL, NULL, NULL, NULL, 4, 4, 4, 4, NULL, NULL, NULL, '{\"type\": \"Theory\", \"save_type\": \"draft\", \"status\": \"draft\", \"is_final\": false, \"test1\": 10.0, \"test2\": 12.0, \"test3\": 14.0, \"best2\": 13.0, \"internal_exam\": 14.0, \"active_learning\": 4.0, \"class_assignment\": 4.0, \"home_assignment\": 4.0, \"attendance\": 4.0, \"total\": 43.0, \"max_marks\": 50.0}'),
(23, 143, 'BCA15226000016', 8, 5, '2026-27', 22, 25, '2026-09-17 23:40:51', '2026-09-17 23:40:51', NULL, NULL, NULL, 9, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 9, NULL, 4, '{\"type\": \"Practical\", \"save_type\": \"final\", \"status\": \"final\", \"is_final\": true, \"internal_exam\": 9.0, \"practical_eval\": 9.0, \"viva\": null, \"journal\": 4.0, \"total\": 22.0, \"max_marks\": 25.0}'),
(24, 149, 'BCA15226000020', 8, 5, '2026-27', 19, 25, '2026-09-17 23:40:51', '2026-09-17 23:40:51', NULL, NULL, NULL, 10, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 5, NULL, 4, '{\"type\": \"Practical\", \"save_type\": \"final\", \"status\": \"final\", \"is_final\": true, \"internal_exam\": 10.0, \"practical_eval\": 5.0, \"viva\": null, \"journal\": 4.0, \"total\": 19.0, \"max_marks\": 25.0}'),
(25, 127, 'BCA15226000001', 7, 5, '2026-27', 21, 25, '2026-09-18 00:39:29', '2026-09-18 00:39:29', NULL, NULL, NULL, 8, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 9, 0, 4, '{\"type\": \"Practical\", \"save_type\": \"draft\", \"status\": \"draft\", \"is_final\": false, \"internal_exam\": 8.0, \"practical_eval\": 9.0, \"viva\": 0.0, \"journal\": 4.0, \"total\": 21.0, \"max_marks\": 25.0}'),
(26, 156, 'BCA15226000023', 5, 5, '2026-27', 43.61, 50, '2026-09-18 09:00:40', '2026-09-18 09:00:40', 15, 15, 18, 46, NULL, NULL, NULL, NULL, 5, 5, 5, 1, NULL, NULL, NULL, '{\"type\": \"Theory\", \"save_type\": \"final\", \"status\": \"final\", \"is_final\": true, \"test1\": 15.0, \"test2\": 15.0, \"test3\": 18.0, \"best2\": 16.5, \"internal_exam\": 46.0, \"active_learning\": 5.0, \"class_assignment\": 5.0, \"home_assignment\": 5.0, \"attendance\": 1.0, \"total\": 43.61, \"max_marks\": 50.0}');

-- --------------------------------------------------------

--
-- Table structure for table `lecture_attendance_sessions`
--

DROP TABLE IF EXISTS `lecture_attendance_sessions`;
CREATE TABLE IF NOT EXISTS `lecture_attendance_sessions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `faculty_id` int NOT NULL,
  `subject_id` int NOT NULL,
  `semester` smallint NOT NULL,
  `division` varchar(10) NOT NULL,
  `academic_year` varchar(20) NOT NULL,
  `lecture_date` date NOT NULL,
  `lecture_no` varchar(50) NOT NULL,
  `status` enum('Draft','Submitted') NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `attendance_mode` enum('Manual','QR') DEFAULT 'Manual',
  `qr_session_token` varchar(255) DEFAULT NULL,
  `qr_session_expires_at` datetime DEFAULT NULL,
  `is_qr_active` tinyint(1) DEFAULT '0',
  `session_type` varchar(20) DEFAULT 'Lecture',
  `start_time` varchar(10) DEFAULT NULL,
  `end_time` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_lecture_session` (`subject_id`,`semester`,`division`,`academic_year`,`lecture_date`,`lecture_no`),
  KEY `faculty_id` (`faculty_id`)
) ENGINE=MyISAM AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `lecture_attendance_sessions`
--

INSERT INTO `lecture_attendance_sessions` (`id`, `faculty_id`, `subject_id`, `semester`, `division`, `academic_year`, `lecture_date`, `lecture_no`, `status`, `created_at`, `updated_at`, `attendance_mode`, `qr_session_token`, `qr_session_expires_at`, `is_qr_active`, `session_type`, `start_time`, `end_time`) VALUES
(1, 11, 3, 4, 'A', '2026-27', '2026-09-16', 'Lecture 1', 'Draft', '2026-09-16 10:53:52', '2026-09-16 10:53:52', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(2, 11, 5, 5, 'A', '2026-27', '2026-09-16', 'Lecture 1', 'Draft', '2026-09-16 10:54:44', '2026-09-16 10:55:51', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(3, 11, 1, 1, 'A', '2026-27', '2026-09-16', 'Lecture 1', 'Submitted', '2026-09-16 10:59:56', '2026-09-16 11:00:10', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(4, 11, 1, 1, 'B', '2026-27', '2026-09-17', 'Lecture 1', 'Submitted', '2026-09-16 11:03:17', '2026-09-16 11:03:17', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(5, 11, 5, 5, 'A', '2026-27', '2026-09-17', 'Lecture 1', 'Submitted', '2026-09-16 11:26:27', '2026-09-16 11:26:27', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(6, 11, 5, 5, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-16 11:27:02', '2026-09-16 11:27:02', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(7, 11, 5, 5, 'A', '2026-27', '2026-09-19', 'Lecture 1', 'Submitted', '2026-09-16 11:27:24', '2026-09-16 11:27:24', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(8, 11, 5, 5, 'A', '2026-27', '2026-09-20', 'Lecture 2', 'Submitted', '2026-09-16 11:27:54', '2026-09-16 11:27:54', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(9, 11, 6, 5, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-18 00:29:05', '2026-09-18 00:29:05', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(10, 11, 6, 5, 'A', '2026-27', '2026-09-19', 'Lecture 1', 'Submitted', '2026-09-18 00:30:57', '2026-09-18 00:30:57', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(11, 11, 6, 5, 'A', '2026-27', '2026-09-20', 'Lecture 1', 'Submitted', '2026-09-18 00:32:10', '2026-09-18 00:32:10', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(12, 11, 6, 5, 'A', '2026-27', '2026-09-21', 'Lecture 1', 'Submitted', '2026-09-18 00:43:39', '2026-09-18 00:43:39', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(13, 11, 5, 5, 'A', '2026-27', '2026-09-25', 'Lecture 1', 'Submitted', '2026-09-18 08:55:02', '2026-09-18 08:55:02', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(14, 11, 8, 5, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-18 10:07:17', '2026-09-18 10:07:17', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(15, 11, 7, 5, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-18 10:07:54', '2026-09-18 10:07:54', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(16, 12, 2, 1, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-18 11:38:03', '2026-09-18 11:38:03', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(17, 12, 10, 1, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-18 11:38:21', '2026-09-18 11:38:21', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(18, 12, 10, 1, 'A', '2026-27', '2026-09-19', 'Lecture 1', 'Submitted', '2026-09-18 11:43:49', '2026-09-18 11:43:49', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(19, 12, 10, 1, 'A', '2026-27', '2026-09-20', 'Lecture 1', 'Submitted', '2026-09-18 11:43:59', '2026-09-18 11:43:59', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(20, 12, 10, 1, 'A', '2026-27', '2026-09-21', 'Lecture 1', 'Submitted', '2026-09-18 11:44:16', '2026-09-18 11:44:16', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(21, 12, 10, 1, 'A', '2026-27', '2026-09-22', 'Lecture 1', 'Submitted', '2026-09-18 11:45:19', '2026-09-18 11:45:19', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(22, 12, 10, 1, 'A', '2026-27', '2026-09-23', 'Lecture 1', 'Submitted', '2026-09-18 11:45:36', '2026-09-18 11:45:36', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(23, 12, 10, 1, 'A', '2026-27', '2026-09-24', 'Lecture 1', 'Submitted', '2026-09-18 11:45:43', '2026-09-18 11:45:43', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(24, 11, 6, 5, 'A', '2026-27', '2026-09-23', 'Lecture 1', 'Submitted', '2026-09-19 03:56:27', '2026-09-19 03:56:27', 'Manual', NULL, NULL, 0, 'Lecture', NULL, NULL),
(25, 6, 1, 2, 'A', '2026-27', '2026-09-25', 'Lecture 1', 'Draft', '2026-09-25 08:31:56', '2026-09-25 09:02:50', 'QR', 'CS-BCA101-A-535A1E', '2026-09-25 14:44:50', 0, 'Lecture', NULL, NULL),
(26, 11, 6, 5, 'A', '2026-27', '2026-09-25', 'Lecture 1', 'Draft', '2026-09-25 08:50:09', '2026-09-25 12:48:12', 'QR', 'CS-BCA501-A-27C3A0', '2026-09-25 18:26:07', 0, 'Lecture', NULL, NULL),
(27, 11, 5, 5, 'A', '2026-27', '2026-09-25', 'Lecture 2', 'Draft', '2026-09-25 12:18:42', '2026-09-25 12:47:41', 'QR', 'CS-BCA501A-A-8F3426', '2026-09-25 18:02:42', 0, 'Lecture', NULL, NULL),
(28, 1, 5, 5, 'A', '2026-27', '2026-09-26', 'Lecture 1', 'Draft', '2026-09-25 20:58:58', '2026-09-26 13:35:19', 'QR', 'CS-BCA501A-A-1A5891', '2026-09-26 22:05:19', 1, 'Lecture', NULL, NULL),
(29, 11, 6, 5, 'A', '2026-27', '2026-09-26', 'Lecture 1', 'Submitted', '2026-09-25 21:45:25', '2026-09-25 23:41:56', 'QR', 'CS-BCA501-A-253D3A', '2026-09-26 05:21:33', 0, 'Lecture', NULL, NULL),
(30, 11, 5, 5, 'A', '2026-27', '2026-09-26', 'Lecture 2', 'Draft', '2026-09-25 23:26:11', '2026-09-25 23:43:05', 'QR', 'CS-BCA501A-A-3E0E30', '2026-09-26 05:22:09', 0, 'Lecture', NULL, NULL),
(31, 11, 6, 5, 'A', '2026-27', '2026-09-27', 'Lecture 1', 'Submitted', '2026-09-26 13:01:20', '2026-09-26 13:40:12', 'QR', 'CS-BCA501-A-1A1C78', '2026-09-26 19:17:57', 0, 'Lecture', NULL, NULL),
(32, 11, 5, 5, 'A', '2026-27', '2026-09-27', 'Lecture 2', 'Submitted', '2026-09-26 13:40:49', '2026-09-26 14:07:33', 'QR', 'CS-BCA501A-A-033BE4', '2026-09-26 19:45:44', 0, 'Lecture', NULL, NULL),
(34, 11, 6, 5, 'A', '2026-27', '2026-09-27', 'Lecture (11:00 - 12:00)', 'Submitted', '2026-09-26 15:33:45', '2026-09-27 06:49:11', 'QR', 'CS-BCA501-A-6E3CAE', '2026-09-27 12:19:11', 0, 'Lecture', '11:00', '12:00'),
(36, 6, 1, 2, 'A', '2026-27', '2026-09-27', 'Lecture 1', 'Draft', '2026-09-27 02:15:48', '2026-09-27 04:23:41', 'QR', 'CS-TEST-TOKEN', '2026-09-27 10:03:41', 1, 'Lecture', NULL, NULL),
(38, 11, 6, 5, 'B', '2026-27', '2026-09-27', 'Lecture (11:00 - 12:00)', 'Draft', '2026-09-27 06:53:10', '2026-09-27 06:53:10', 'QR', 'CS-BCA501-B-CE4F21', '2026-09-27 12:33:10', 1, 'Lecture', '11:00', '12:00');

-- --------------------------------------------------------

--
-- Table structure for table `lecture_attendance_students`
--

DROP TABLE IF EXISTS `lecture_attendance_students`;
CREATE TABLE IF NOT EXISTS `lecture_attendance_students` (
  `id` int NOT NULL AUTO_INCREMENT,
  `session_id` int NOT NULL,
  `student_id` int NOT NULL,
  `status` enum('Present','Absent') NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `marked_method` varchar(30) DEFAULT 'MANUAL',
  `scanned_at` datetime DEFAULT NULL,
  `device_fingerprint` varchar(500) DEFAULT NULL,
  `scan_latitude` decimal(10,8) DEFAULT NULL,
  `scan_longitude` decimal(11,8) DEFAULT NULL,
  `distance_meters` float DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_session_student_attendance` (`session_id`,`student_id`),
  KEY `student_id` (`student_id`)
) ENGINE=MyISAM AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `lecture_attendance_students`
--

INSERT INTO `lecture_attendance_students` (`id`, `session_id`, `student_id`, `status`, `created_at`, `updated_at`, `marked_method`, `scanned_at`, `device_fingerprint`, `scan_latitude`, `scan_longitude`, `distance_meters`, `is_verified`) VALUES
(1, 1, 144, 'Present', '2026-09-16 10:53:52', '2026-09-16 10:53:52', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(2, 1, 145, 'Absent', '2026-09-16 10:53:52', '2026-09-16 10:53:52', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(3, 1, 146, 'Absent', '2026-09-16 10:53:52', '2026-09-16 10:53:52', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(4, 2, 143, 'Present', '2026-09-16 10:54:44', '2026-09-16 11:25:38', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(5, 2, 149, 'Absent', '2026-09-16 10:54:44', '2026-09-16 10:54:44', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(6, 3, 127, 'Absent', '2026-09-16 10:59:56', '2026-09-16 11:00:10', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(7, 3, 128, 'Present', '2026-09-16 10:59:56', '2026-09-16 10:59:56', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(8, 3, 129, 'Absent', '2026-09-16 10:59:56', '2026-09-16 11:00:10', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(9, 3, 131, 'Absent', '2026-09-16 10:59:56', '2026-09-16 11:00:10', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(10, 3, 134, 'Present', '2026-09-16 10:59:56', '2026-09-16 10:59:56', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(11, 3, 135, 'Present', '2026-09-16 10:59:56', '2026-09-16 10:59:56', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(12, 3, 138, 'Absent', '2026-09-16 10:59:56', '2026-09-16 11:00:10', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(13, 3, 139, 'Present', '2026-09-16 10:59:56', '2026-09-16 10:59:56', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(14, 4, 132, 'Present', '2026-09-16 11:03:17', '2026-09-16 11:03:17', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(15, 4, 133, 'Absent', '2026-09-16 11:03:17', '2026-09-16 11:03:17', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(16, 4, 137, 'Absent', '2026-09-16 11:03:17', '2026-09-16 11:03:17', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(17, 4, 140, 'Present', '2026-09-16 11:03:17', '2026-09-16 11:03:17', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(18, 5, 143, 'Present', '2026-09-16 11:26:27', '2026-09-16 11:26:27', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(19, 5, 149, 'Present', '2026-09-16 11:26:27', '2026-09-16 11:26:27', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(20, 6, 143, 'Absent', '2026-09-16 11:27:02', '2026-09-16 11:27:02', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(21, 6, 149, 'Present', '2026-09-16 11:27:02', '2026-09-16 11:27:02', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(22, 7, 143, 'Present', '2026-09-16 11:27:24', '2026-09-16 11:27:24', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(23, 7, 149, 'Present', '2026-09-16 11:27:24', '2026-09-16 11:27:24', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(24, 8, 143, 'Present', '2026-09-16 11:27:54', '2026-09-16 11:27:54', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(25, 8, 149, 'Present', '2026-09-16 11:27:54', '2026-09-16 11:27:54', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(26, 9, 143, 'Present', '2026-09-18 00:29:05', '2026-09-18 00:29:05', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(27, 9, 149, 'Present', '2026-09-18 00:29:05', '2026-09-18 00:29:05', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(28, 10, 143, 'Present', '2026-09-18 00:30:57', '2026-09-18 00:30:57', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(29, 10, 149, 'Present', '2026-09-18 00:30:57', '2026-09-18 00:30:57', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(30, 11, 143, 'Present', '2026-09-18 00:32:10', '2026-09-18 00:32:10', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(31, 11, 149, 'Present', '2026-09-18 00:32:10', '2026-09-18 00:32:10', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(32, 12, 143, 'Present', '2026-09-18 00:43:39', '2026-09-18 00:43:39', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(33, 12, 149, 'Present', '2026-09-18 00:43:39', '2026-09-18 00:43:39', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(34, 13, 156, 'Present', '2026-09-18 08:55:02', '2026-09-18 08:55:02', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(35, 14, 156, 'Present', '2026-09-18 10:07:17', '2026-09-18 10:07:17', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(36, 15, 156, 'Present', '2026-09-18 10:07:54', '2026-09-18 10:07:54', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(58, 24, 204, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(57, 24, 203, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(56, 24, 202, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(55, 24, 201, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(54, 24, 200, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(53, 24, 156, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(59, 25, 127, 'Present', '2026-09-25 08:31:56', '2026-09-25 08:31:56', 'QR', '2026-09-25 14:01:56', 'DEV-TEST-PHONE-1', 24.15960000, 72.40300000, 8.42081, 1),
(60, 26, 156, 'Present', '2026-09-25 09:43:57', '2026-09-25 11:09:13', 'QR', '2026-09-25 16:39:13', 'DEV-VM9L63RN-MUH6QKXB', NULL, NULL, 0, 1),
(61, 26, 200, 'Present', '2026-09-25 09:43:57', '2026-09-25 12:12:34', 'QR', '2026-09-25 17:42:34', 'DEV-CHIRAG-OWN-PHONE-999', 24.16216216, 72.39668186, 699.99, 1),
(62, 26, 201, 'Present', '2026-09-25 09:43:57', '2026-09-25 11:25:19', 'QR', '2026-09-25 16:55:19', 'DEV-HETVI-TEST-PHONE', 24.16216216, 72.39668186, 699.99, 1),
(63, 26, 202, 'Absent', '2026-09-25 09:43:57', '2026-09-25 09:43:57', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(64, 26, 203, 'Absent', '2026-09-25 09:43:57', '2026-09-25 09:43:57', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(65, 26, 204, 'Absent', '2026-09-25 09:43:57', '2026-09-25 09:43:57', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(66, 27, 156, 'Present', '2026-09-25 12:19:29', '2026-09-25 12:19:29', 'QR', '2026-09-25 17:49:29', 'DEV-VM9L63RN-MUH6QKXB', 24.16216216, 72.39668186, 699.99, 1),
(67, 27, 200, 'Present', '2026-09-25 12:22:46', '2026-09-25 12:22:46', 'QR', '2026-09-25 17:52:46', 'DEV-VM9L63RN-MUH6QKXB', NULL, NULL, NULL, 1),
(70, 29, 201, 'Absent', '2026-09-25 21:46:03', '2026-09-25 21:46:03', 'REJECTED_PROXY', NULL, NULL, NULL, NULL, NULL, 0),
(71, 29, 200, 'Present', '2026-09-25 21:46:37', '2026-09-25 21:46:37', 'QR', '2026-09-26 03:16:37', 'DEV-URARHCM9-MUHA8SVC', 24.15956670, 72.40287750, 8.33176, 1),
(72, 29, 156, 'Present', '2026-09-25 21:49:00', '2026-09-25 21:49:00', 'QR', '2026-09-26 03:19:00', 'DEV-U7CYYMC7-MUHQK77Z', 24.15956250, 72.40291520, 4.74724, 1),
(73, 29, 202, 'Present', '2026-09-25 21:52:12', '2026-09-25 21:52:12', 'QR', '2026-09-26 03:22:12', 'DEV-0FIZNV46-MUHTOV6F', 24.15956350, 72.40291920, 4.49536, 1),
(74, 29, 203, 'Absent', '2026-09-25 23:41:45', '2026-09-25 23:41:45', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(75, 29, 204, 'Absent', '2026-09-25 23:41:45', '2026-09-25 23:41:45', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(76, 30, 156, 'Absent', '2026-09-25 23:43:05', '2026-09-25 23:43:05', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(77, 30, 200, 'Absent', '2026-09-25 23:43:05', '2026-09-25 23:43:05', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(78, 30, 201, 'Absent', '2026-09-25 23:43:05', '2026-09-25 23:43:05', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(79, 30, 202, 'Absent', '2026-09-25 23:43:05', '2026-09-25 23:43:05', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(80, 30, 203, 'Absent', '2026-09-25 23:43:05', '2026-09-27 06:54:00', 'REJECTED_PROXY', NULL, NULL, NULL, NULL, NULL, 0),
(81, 30, 204, 'Absent', '2026-09-25 23:43:05', '2026-09-25 23:43:05', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(82, 31, 156, 'Absent', '2026-09-26 13:04:46', '2026-09-26 13:04:46', 'REJECTED_PROXY', NULL, NULL, NULL, NULL, NULL, 0),
(83, 31, 200, 'Absent', '2026-09-26 13:04:51', '2026-09-26 13:04:51', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(84, 31, 201, 'Absent', '2026-09-26 13:04:51', '2026-09-26 13:04:51', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(85, 31, 202, 'Absent', '2026-09-26 13:04:51', '2026-09-26 13:04:51', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(86, 31, 203, 'Absent', '2026-09-26 13:04:51', '2026-09-26 13:04:51', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(87, 31, 204, 'Absent', '2026-09-26 13:04:51', '2026-09-26 13:04:51', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(88, 32, 156, 'Present', '2026-09-26 13:41:27', '2026-09-26 13:41:27', 'QR', '2026-09-26 19:11:27', 'ATjSNRsq0IIRZPGnMgu2ye69kdlFmEzvwmsiftMVQse8gyMsNS8NQMs8lyRUp9siTXYg_usbK4eDlRoGgdN8AuE', 24.15959550, 72.40263260, 33.1528, 1),
(89, 32, 200, 'Absent', '2026-09-26 13:46:40', '2026-09-26 13:46:40', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(90, 32, 201, 'Absent', '2026-09-26 13:46:40', '2026-09-26 13:46:40', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(91, 32, 202, 'Absent', '2026-09-26 13:46:40', '2026-09-26 13:46:40', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(92, 32, 203, 'Absent', '2026-09-26 13:46:40', '2026-09-26 13:46:40', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(93, 32, 204, 'Absent', '2026-09-26 13:46:40', '2026-09-26 13:46:40', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(94, 34, 156, 'Present', '2026-09-26 15:33:57', '2026-09-27 03:16:40', 'QR', '2026-09-27 08:46:40', 'ATjSNRsq0IIRZPGnMgu2ye69kdlFmEzvwmsiftMVQse8gyMsNS8NQMs8lyRUp9siTXYg_usbK4eDlRoGgdN8AuE', 24.15955660, 72.40292830, 3.29495, 1),
(95, 34, 200, 'Absent', '2026-09-26 15:33:57', '2026-09-27 06:27:06', 'REJECTED_PROXY', NULL, NULL, NULL, NULL, NULL, 0),
(96, 34, 201, 'Absent', '2026-09-26 15:33:57', '2026-09-26 15:33:57', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(97, 34, 202, 'Absent', '2026-09-26 15:33:57', '2026-09-26 15:33:57', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(98, 34, 203, 'Absent', '2026-09-26 15:33:57', '2026-09-26 15:33:57', 'Manual', NULL, NULL, NULL, NULL, NULL, 1),
(99, 34, 204, 'Absent', '2026-09-26 15:33:57', '2026-09-26 15:33:57', 'Manual', NULL, NULL, NULL, NULL, NULL, 1);

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(200) NOT NULL,
  `message` text NOT NULL,
  `category` varchar(50) NOT NULL,
  `photo_file` varchar(255) DEFAULT NULL,
  `file_type` varchar(20) DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `end_date` datetime DEFAULT NULL,
  `posted_by_role` enum('Admin','Faculty') NOT NULL,
  `admin_id` int DEFAULT NULL,
  `faculty_id` int DEFAULT NULL,
  `target_audience` enum('All','Guest','Faculty','Student') NOT NULL,
  `target_semester` smallint DEFAULT NULL,
  `target_division` varchar(10) DEFAULT NULL,
  `subject_id` int DEFAULT NULL,
  `priority` enum('Normal','Important','Urgent') NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `is_final_saved` tinyint(1) NOT NULL DEFAULT '0',
  `final_saved_at` datetime DEFAULT NULL,
  `final_saved_by` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `admin_id` (`admin_id`),
  KEY `faculty_id` (`faculty_id`),
  KEY `subject_id` (`subject_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `title`, `message`, `category`, `photo_file`, `file_type`, `start_date`, `end_date`, `posted_by_role`, `admin_id`, `faculty_id`, `target_audience`, `target_semester`, `target_division`, `subject_id`, `priority`, `is_active`, `created_at`, `updated_at`, `is_final_saved`, `final_saved_at`, `final_saved_by`) VALUES
(6, 'unit 1 to 4 All', '### Notice Instructions & Guidelines\r\n\r\nPlease read all notices carefully and follow the instructions provided by the college or faculty.\r\n\r\n* Check the notice regularly for important updates.\r\n* Follow the given instructions, deadlines, and schedules.\r\n* Make sure to attend required classes, events, or activities on time.\r\n* If any document or form is required, submit it before the specified deadline.\r\n* Contact the concerned faculty or administrator if you have any questions or need clarification.\r\n* Do not ignore important or urgent notices.\r\n* Keep your contact information updated to receive important notifications.\r\n\r\n**Important:** Students are responsible for checking notices regularly and following the instructions mentioned in them.', 'Assignment Submit Date', '91d31ebaaa_Assignment_Questions_.Net_GUI_App.pdf', 'document', '2026-09-26 20:01:00', '2026-09-27 09:02:00', 'Faculty', NULL, 11, 'Student', 5, 'A', 5, 'Normal', 1, '2026-09-26 03:33:46', '2026-09-26 03:33:46', 0, NULL, NULL),
(2, 'Assignment 3 - Database Indexing', 'Complete the SQL indexing assignment.', 'Assignment Submit Date', NULL, NULL, '2026-09-25 02:46:44', '2026-09-27 14:46:44', 'Faculty', NULL, NULL, 'Student', 2, 'A', NULL, 'Urgent', 1, '2026-09-25 15:46:44', '2026-09-26 02:04:18', 0, NULL, NULL),
(7, 'Exam Timetable', '### Notice Instructions & Guidelines\r\n\r\nPlease read all notices carefully and follow the instructions provided by the college or faculty.\r\n\r\n* Check the notice regularly for important updates.\r\n* Follow the given instructions, deadlines, and schedules.\r\n* Make sure to attend required classes, events, or activities on time.\r\n* If any document or form is required, submit it before the specified deadline.\r\n* Contact the concerned faculty or administrator if you have any questions or need clarification.\r\n* Do not ignore important or urgent notices.\r\n* Keep your contact information updated to receive important notifications.\r\n\r\n**Important:** Students are responsible for checking notices regularly and following the instructions mentioned in them.', 'Exam', 'dee26581be_Screenshot_2026-05-09_054844.png', 'image', '2026-09-26 20:13:00', '2026-09-27 09:14:00', 'Admin', 1, NULL, 'Guest', NULL, 'All', NULL, 'Urgent', 1, '2026-09-26 03:43:50', '2026-09-26 03:43:50', 0, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `result_declarations`
--

DROP TABLE IF EXISTS `result_declarations`;
CREATE TABLE IF NOT EXISTS `result_declarations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `academic_year` varchar(20) NOT NULL,
  `semester` smallint NOT NULL,
  `division` varchar(10) NOT NULL,
  `is_declared` tinyint(1) NOT NULL,
  `declared_at` datetime DEFAULT NULL,
  `declared_by` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_result_decl_ay_sem_div` (`academic_year`,`semester`,`division`),
  KEY `declared_by` (`declared_by`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `result_declarations`
--

INSERT INTO `result_declarations` (`id`, `academic_year`, `semester`, `division`, `is_declared`, `declared_at`, `declared_by`, `created_at`, `updated_at`) VALUES
(1, '2026-27', 5, 'All', 0, '2026-09-18 15:38:11', 1, '2026-09-18 10:02:09', '2026-09-18 10:31:01'),
(2, '2026-27', 1, 'All', 0, '2026-09-18 15:50:37', 1, '2026-09-18 10:11:12', '2026-09-18 10:20:37');

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

DROP TABLE IF EXISTS `students`;
CREATE TABLE IF NOT EXISTS `students` (
  `id` int NOT NULL AUTO_INCREMENT,
  `roll_number` varchar(20) NOT NULL,
  `enrollment_no` varchar(20) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `mobile` varchar(15) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `course` varchar(50) DEFAULT NULL,
  `semester` smallint DEFAULT NULL,
  `division` varchar(10) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `profile_photo` varchar(255) DEFAULT NULL,
  `status` enum('Active','Inactive') DEFAULT NULL,
  `password_changed` smallint DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `academic_year` varchar(20) DEFAULT NULL,
  `reset_otp` varchar(255) DEFAULT NULL,
  `otp_expiry` datetime DEFAULT NULL,
  `otp_attempts` int NOT NULL DEFAULT '0',
  `otp_blocked_until` datetime DEFAULT NULL,
  `device_fingerprint` varchar(500) DEFAULT NULL,
  `device_model` varchar(100) DEFAULT NULL,
  `device_bound_at` datetime DEFAULT NULL,
  `device_reset_allowed` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `enrollment_no` (`enrollment_no`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `uq_academic_course_sem_roll` (`academic_year`,`course`,`semester`,`roll_number`)
) ENGINE=MyISAM AUTO_INCREMENT=206 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id`, `roll_number`, `enrollment_no`, `full_name`, `email`, `mobile`, `dob`, `course`, `semester`, `division`, `password`, `profile_photo`, `status`, `password_changed`, `last_login`, `created_at`, `updated_at`, `academic_year`, `reset_otp`, `otp_expiry`, `otp_attempts`, `otp_blocked_until`, `device_fingerprint`, `device_model`, `device_bound_at`, `device_reset_allowed`) VALUES
(127, '1', 'BCA15226000001', 'Aarav Patel', 'aarav.patel@college.edu', '9825012345', '2005-05-12', 'BCA', 2, 'A', 'scrypt:32768:8:1$NKUxoUQhJMCsHZgW$7b107b269644e597703f6844a2b760b549f18a1ef79b5a80dc8afca4a0aa899b991a1da8bc8b5bb9c6a79f2c3f27da25ec4676c91c0e6c5b291850f373a83d9f', 'default-avatar.png', 'Active', 0, '2026-09-25 15:49:02', '2026-08-16 04:26:49', '2026-09-27 04:23:42', '2026-27', NULL, NULL, 0, NULL, 'MY-OLD-PHONE', 'Pixel 8', '2026-09-27 09:53:42', 0),
(128, '2', 'BCA15226000002', 'Aditya Vaghela', 'aditya.vaghela@college.edu', '9377122334', '2005-10-02', 'BCA', 2, 'A', 'scrypt:32768:8:1$DnjFUr06xgjjqA5N$ce5bca11cdffa6a97859705a5bee9d48ea7cba38fd76ee3f691ad1b39936d9d2bc25d0773b5d5cff648344434f13c8af16a10cb2de8169119b02fdbe5107e556', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:50', '2026-09-27 04:22:30', '2026-27', NULL, NULL, 0, NULL, 'FRIEND-PHONE-FINGERPRINT', NULL, NULL, 0),
(129, '3', 'BCA15226000003', 'Bhavya Patel', 'bhavya.patel@college.edu', '9765432109', '2005-12-01', 'BCA', 2, 'A', 'scrypt:32768:8:1$2VRFvG9GgoaivAqv$eb80d89aed60253e2e371ed038a39a1362e8469b6261ec5d99c02dfd18cbe795cec427727e5c01bc9a3b06fa54b7bc0a5be5ca4d9367c1826c8bd94354ff8f66', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:50', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(130, '4', 'BCA15226000004', 'Dev Shah', 'dev.shah@college.edu', '9898765432', '2005-03-30', 'BCA', 2, 'C', 'scrypt:32768:8:1$nDj390rGKqHtFdnW$b2776fff3cdfd8e1f4ae9e4b44e3a3d2308c9e2503cafc3441eb256eebc4eb4090e169df7ba8c426109295aea1a1fee256be44f915f7d47e4530bab1c6cfd020', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:50', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(131, '5', 'BCA15226000005', 'Diya Shah', 'diya.shah@college.edu', '9909988776', '2005-08-22', 'BCA', 2, 'A', 'scrypt:32768:8:1$HbqvOmUE7D0WtRYy$dc9617a31144470ee0786f02b0f39b500f38b262e43a91e016ac680674500ee6ffc1f3001bd51c25dcc5e7e289001914de61c4970f1d1c12aa07b6df8845fa8d', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:50', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(132, '6', 'BCA15226000006', 'Harsh Mehta', 'harsh.mehta@college.edu', '9712345678', '2004-11-05', 'BCA', 2, 'B', 'scrypt:32768:8:1$KHcSGiGLJEh0WYx0$6063458dcf633df3830ff2207cbe3ca6ef5203554a4348af1333bf1efed1e6e3ed6bdca3f97785a4e6eaf80e6b75adbccccc8ecddb5166bd8332ace22d9ab50c', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:51', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(133, '7', 'BCA15226000007', 'Janvi Chawla', 'janvi.chawla@college.edu', '9638055667', '2006-05-17', 'BCA', 2, 'B', 'scrypt:32768:8:1$YSRAlcwaWbNjX10C$e7a847d5b5d6394fc84044a0cfa5ed493a7cfed0e7a515ea946971b43b554a25878d9f5522515318b8f874a6125c647f18aad62d2daf23086be7226c9573c438', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:51', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(134, '8', 'BCA15226000008', 'Karan Rajput', 'karan.rajput@college.edu', '9879011223', '2004-10-28', 'BCA', 2, 'A', 'scrypt:32768:8:1$XrVulzA4ajm56DMY$633306221ac536819afb5b8b37140f7f2f602f4eb49b2a8f99eef132f4482d3d3ac94c398c31d182bd0224a74cfa92265e39143bc4f89723d24752760ccb5d5e', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:51', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(135, '9', 'BCA15226000009', 'Kavya Trivedi', 'kavya.trivedi@college.edu', '9723456789', '2004-09-14', 'BCA', 2, 'A', 'scrypt:32768:8:1$UbJKWbygTxADew2r$d499541af9cafeeefec1fc2128e360986825df9315c7dca5aa6fbe9aab2864acea602a82ee75d44517f11261d039322d8d9526e6a739b99a0621e0ad93e28a69', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:52', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(136, '10', 'BCA15226000010', 'Nidhi Parmar', 'nidhi.parmar@college.edu', '9426033445', '2004-12-08', 'BCA', 2, 'C', 'scrypt:32768:8:1$edxVNydkf6inJvPa$42411800ba20bdb9edc60d3ce453eabe458baacef4dca0f8684e193b4813e813b74a1ccce29d3686f87b550e14a3604bb5deac4a2e42867cbfa54f1bf957d2f6', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:52', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(137, '11', 'BCA15226000011', 'Pooja Dave', 'pooja.dave@college.edu', '9662011223', '2006-01-25', 'BCA', 2, 'B', 'scrypt:32768:8:1$hTuaYKj4O67ooGNe$d2a90923170e5ef3918d2c7667aee4b131b34dae2b6d12ab13cfd23947a1f332ff5b7b0e9d002a7055eb87f35d1cf993db73404934d935a4602a6ab82749f135', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:52', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(138, '12', 'BCA15226000012', 'Riya Sharma', 'riya.sharma@college.edu', '9876543210', '2006-02-18', 'BCA', 2, 'A', 'scrypt:32768:8:1$SmERAQldvJ2YmoGQ$9563cd8d69ec6c9001a137e78cf45a42db9afe0188948e81a6b2912e24917f7bacb1235b35100fb0012c5a7cacb9f2b4d397e62623b11852b9dee9b3e4d4a19f', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:52', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(139, '13', 'BCA15226000013', 'Rohan Joshi', 'rohan.joshi@college.edu', '9558877665', '2005-07-19', 'BCA', 2, 'A', 'scrypt:32768:8:1$5FaxpS0acS1Gtc30$59b5d2fd56d70f949644b4b008c774bdafa40f46cbba37d1f86ebf38fde84cdf9a286a3e10234dff0dd04a58b5876c08962fd3a1fa5a7d9a0e569b381b655942', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:53', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(140, '14', 'BCA15226000014', 'Siddharth Desai', 'siddharth.desai@college.edu', '9106055443', '2006-04-11', 'BCA', 2, 'B', 'scrypt:32768:8:1$IxSYCMRmJSbhVdiQ$ce4cd315d8697512ac87fd7adc1cafd822094133c1224f6c67e8a7dcd6de34bf40bbbbc1b0026678bdd565e4bcca9c555cfb79323e4010e6dc41f8582dee9dd8', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:53', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(141, '15', 'BCA15226000015', 'Tanvi Solanki', 'tanvi.solanki@college.edu', '9998877661', '2005-06-15', 'BCA', 2, 'C', 'scrypt:32768:8:1$AaedyGeyz8mEqntC$68de85f0ab98378c990cbbe64e36f13955f7346b3143b8274a1f5acf948660c8da1885d9915d9b22618659341758b1ecbb5e21fe4bea6a182adcbe61954449b9', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:54', '2026-09-18 08:38:13', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(143, '1', 'BCA15226000016', 'akash raval', 'akashraval3709@gmail.com', '9328976260', '2006-10-10', 'BCA', 6, 'A', 'scrypt:32768:8:1$qvABZku1NVI4oW75$1c57051868b0f3cda982f8815ccaff8b20382e85d5a70eb491b74524a2638919c4f8b4354072d01477ea75dadd1523e3faf8676167b8edbc89bd90c066f24424', 'default-avatar.png', 'Active', 0, '2026-09-19 02:14:27', '2026-09-13 09:53:27', '2026-09-18 20:44:27', '2024-25', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(144, '1', 'BCA15226000017', 'piyush', 'piyush@gmail.com', '9904089637', '2011-03-16', 'BCA', 4, 'A', 'scrypt:32768:8:1$lNW6qqQVfrysUuKt$58bcd44d1cf63aaebbc554672e1da1ae8d14f64b90d0f00e57c353cf3bddf680f19dc5a58259e550b6d8a844a6919d09a0053f54c448b4358340482c87d2fade', 'default-avatar.png', 'Active', 0, NULL, '2026-09-13 21:44:43', '2026-09-18 08:38:13', '2025-26', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(145, '2', 'BCA15226000018', 'akash r', 'nandni.devloper17@gmail.com', '9328322901', '2001-06-05', 'BCA', 4, 'A', 'scrypt:32768:8:1$HwaR1pGXGuxuTY0M$3466ada68dc2990427f3dd7f5d857164a4aa5cd5aadba8bb0f40438fbc6f644e37cb42e34b005c2ee045c8ec500d79aebe6d5f4eb92a3f9a026c61962578cf87', 'default-avatar.png', 'Active', 0, '2026-09-14 09:40:39', '2026-09-14 04:09:17', '2026-09-18 08:38:13', '2025-26', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(146, '3', 'BCA15226000019', 'akash r', 'nandni@gmail.com', '9328322902', '2001-06-05', 'BCA', 4, 'A', 'scrypt:32768:8:1$EJrZuTyzVELMnvPY$c5daf3d539468535418f7fcb2dc9db06c2a0901d227e17ea51207fa5d95fcf257bb471c28d235f206720007bd220ab5a71b0ee3da5d0a208c9cabf9043103cdc', 'default-avatar.png', 'Active', 0, NULL, '2026-09-14 04:21:10', '2026-09-18 08:38:13', '2025-26', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(149, '2', 'BCA15226000020', 'DEVIDKUMAR DANABHAI PARMAR', 'devidparmar8954@gmail.com', '9054702563', '2006-09-17', 'BCA', 6, 'A', 'scrypt:32768:8:1$ZOd1XKntwVL6gacB$a50b526198f91a303404201c3d6e24ecde599aa8b40a180512c2c003c75d0c7ac0866600a7d3031e62e3eae585f1163a7be21a91e5b6c692d7184800791a6b80', 'default-avatar.png', 'Active', 0, NULL, '2026-09-16 08:05:36', '2026-09-18 08:38:13', '2024-25', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(156, '6', 'BCA15226000023', 'Sachin Rathod', 'sachin123@gmail.com', '8980870263', '2005-08-01', 'BCA', 5, 'A', 'scrypt:32768:8:1$RUtZFi9ahMsWebkh$1965365c1cd2f0e9314b8150eefd67ffb2b57764846710382419403d9c414c01d23e29f77ac499335a2e0cc92ab10d45407626f70e975721d0034c9c7b258ea2', 'default-avatar.png', 'Active', 0, '2026-09-27 09:17:45', '2026-09-18 08:23:03', '2026-09-27 03:47:45', '2024-25', NULL, NULL, 0, NULL, 'ATjSNRsq0IIRZPGnMgu2ye69kdlFmEzvwmsiftMVQse8gyMsNS8NQMs8lyRUp9siTXYg_usbK4eDlRoGgdN8AuE', 'Android Phone', '2026-09-26 19:11:27', 0),
(204, '5', 'BCA15226000037', 'Urvi Thakkar', 'urvi.thakkar505@campussync.edu', '9870005005', '2004-07-04', 'BCA', 5, 'A', 'scrypt:32768:8:1$LllrtDoLND7qf6rG$252d3372915c2677b4b64b72f8ca812b7e2b87cd050da90a7b1c2e2ad4ef0ba77cede4569c30fda1f3d54554e47046a9f0fd6c2e348849822eca44559cd19a39', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:55', '2026-09-19 02:15:55', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(203, '4', 'BCA15226000036', 'Nirav Prajapati', 'nirav.prajapati504@campussync.edu', '9870005004', '2003-11-12', 'BCA', 5, 'A', 'scrypt:32768:8:1$51vLajAmXhrRkab9$e35c743e4b2fc824c45e33dea0e62330d9b053ea5d3834b09431690ac0d6656f26870890b6e22bec0259af880eba65d24357a8a4776e6c1b578f1cfd55bd35b8', 'default-avatar.png', 'Active', 0, '2026-09-26 05:10:50', '2026-09-19 02:15:55', '2026-09-25 23:40:50', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, '2026-09-26 05:05:26', 0),
(202, '3', 'BCA15226000035', 'Manan Shukla', 'manan.shukla503@campussync.edu', '9870005003', '2004-03-21', 'BCA', 5, 'A', 'scrypt:32768:8:1$kHuTPd97nGUNZnXj$40a1b0d72edc4d5a2b4757aa9ff736ab88300cb74c7df8fecc5c7bf2bd7a044e5b4367dad54dd21017f1a67351b5d56ce2cd1a9e4a6dc116bd074d87de961ce6', 'default-avatar.png', 'Active', 0, '2026-09-27 09:28:58', '2026-09-19 02:15:54', '2026-09-27 03:58:58', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(201, '2', 'BCA15226000034', 'Hetvi Vora', 'hetvi.vora502@campussync.edu', '9870005002', '2004-10-08', 'BCA', 5, 'A', 'scrypt:32768:8:1$wAFsrxbav0TmZnvB$e2b61de283b40d2bcc14a84a9cc3adef39e5f43c1518f463c48a0e192be23105fa794ca6a14172591095537a762ce56972bf2f50ad95c6c23c39a29c94b8777e', 'default-avatar.png', 'Active', 0, '2026-09-26 03:50:47', '2026-09-19 02:15:54', '2026-09-25 22:20:47', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, '2026-09-26 03:47:54', 0),
(200, '1', 'BCA15226000033', 'Chirag Panchal', 'chirag.panchal501@campussync.edu', '9870005001', '2004-05-16', 'BCA', 5, 'A', 'scrypt:32768:8:1$0x0k70khqKhM47GE$2a635adcae77f2f7667a94013afba0f1dabbd80ae2456093be5e36272744cd750f9eccbe29b96053299556cc5cee6cb8fc6f69356855b3e2f5831849c019fbcd', 'default-avatar.png', 'Active', 0, '2026-09-27 09:30:59', '2026-09-19 02:15:54', '2026-09-27 04:00:59', '2026-27', NULL, NULL, 0, NULL, 'AcpXFkUN_-WkYQW7_SRqHBafpDsAcZHr_CLmslw_WFRIoCYo7Joxhl---wcY5zVTt6OugBm8V0BL-aBQdKlwTwM', 'Mobile Device', '2026-09-27 09:25:00', 0),
(199, '5', 'BCA15226000032', 'Yash Barot', 'yash.barot305@campussync.edu', '9870003005', '2005-06-19', 'BCA', 3, 'A', 'scrypt:32768:8:1$H6l3CbJPRRnyckgl$6c2d007015beb89f76120840bcebf5af17f0c868d1d2c673eb0b774e431ad80cc256205e0d9852c6e653cbb8422cb206f1efd281b39924802a84f3e60e3ef6ec', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-19 02:15:54', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(198, '4', 'BCA15226000031', 'Prachi Soni', 'prachi.soni304@campussync.edu', '9870003004', '2004-12-25', 'BCA', 3, 'A', 'scrypt:32768:8:1$9VwCATxuOLXqBnVx$c204ae379aeac08fd1b436e060ddd842f1a34fee51372739b78370dbd1fe83d010f4dbc37dbc047cc17117dbe8b21b596cf6ea71db31dc592847cc5e8ad18693', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-19 02:15:54', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(197, '3', 'BCA15226000030', 'Mihir Dave', 'mihir.dave303@campussync.edu', '9870003003', '2005-02-14', 'BCA', 3, 'A', 'scrypt:32768:8:1$9CmsJ80eev8z6VDF$a90ecb419ea95343c967161d097052604dd3197c8a6c408a01640e189eabc07bdb1a66ff3056023f0136947457daefa23094d104d265a6b16aa6fa389732e011', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-19 02:15:54', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(196, '2', 'BCA15226000029', 'Kiran Zala', 'kiran.zala302@campussync.edu', '9870003002', '2005-08-30', 'BCA', 3, 'A', 'scrypt:32768:8:1$r8iYfu6bDMT6dgaD$0c6a7e28336cbcb1837d3910d691505a4189cd567a407423d5f69af774390bdb6b4e350402340a4290498138fe87a73f635b6b87d01a904d9ea8ac93f6c95a0e', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-19 02:15:54', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(195, '1', 'BCA15226000028', 'Devansh Pandya', 'devansh.pandya301@campussync.edu', '9870003001', '2005-04-12', 'BCA', 3, 'A', 'scrypt:32768:8:1$peXk4JuUtkEl4X7c$5042a5e6c0812cd9e99cecae835b032d76e7f1ce33624d1f0f03141efd22a547021e3cfad917798a5702a2490464e9f9d2fd04a5f13e4e3e6e824fe10eb41734', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-19 02:15:54', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(194, '5', 'BCA15226000027', 'Pooja Rathod', 'pooja.rathod105@campussync.edu', '9870001005', '2006-09-18', 'BCA', 1, 'A', 'scrypt:32768:8:1$PyeSN1ppbOLJTCe6$a7cb96b6cca32ad846f6aa5f736981679b28261ac22099f5ed895ac5f27050943a0ea333ab6234657be1fbb93a4b37f6a474c149671c1ae0da95f0ad4e2f053c', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-19 02:15:54', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(193, '4', 'BCA15226000026', 'Meet Shah', 'meet.shah104@campussync.edu', '9870001004', '2005-11-05', 'BCA', 1, 'A', 'scrypt:32768:8:1$ldj8H3FIgZR836E1$df57a0604c1470b6778ba2c82edce477d7ce1110934c69d82ed112705c8359e26ba84bfd5d1caf8a704473064308fa6d848a79c08fa0cb7a41fa3d8cf5d6ce01', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:53', '2026-09-19 02:15:53', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(192, '3', 'BCA15226000025', 'Khushi Patel', 'khushi.patel103@campussync.edu', '9870001003', '2006-01-10', 'BCA', 1, 'A', 'scrypt:32768:8:1$0Nk1zI9TYsMCKTYy$a6bc028cfe2a5d46b01a36a2ca9d7a2a437a174addaa09c234076d75e98948fc6cc28b3ed32b144631484ae7763ef58a5f6226beaad5d61f7286839843be812e', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:53', '2026-09-19 02:15:53', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(191, '2', 'BCA15226000024', 'Dhruv Mehta', 'dhruv.mehta102@campussync.edu', '9870001002', '2006-07-22', 'BCA', 1, 'A', 'scrypt:32768:8:1$cWBaP0PeKs5tjqxY$fb8291fb79c930e76fc06fa0d97c9558243050bc018c9b8970b06d2a439a88e96f9dded8579cbdb3c2d9c7164f6e034eba37173823ca8bf3cb99f009f23c37db', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:53', '2026-09-19 02:15:53', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(190, '1', 'BCA15226000022', 'Aayush Joshi', 'aayush.joshi101@campussync.edu', '9870001001', '2006-03-15', 'BCA', 1, 'A', 'scrypt:32768:8:1$3IurQynzm9kaJKOp$1843cf3023fbd7c60badbe1499e70917f91e276b6b359cbc09063f7f6845a5d017fa987863af86c68136422f7950e54082f94b2ff63173f06f37b1437a5a2c1a', 'default-avatar.png', 'Active', 0, '2026-09-19 07:46:12', '2026-09-19 02:15:53', '2026-09-19 02:16:12', '2026-27', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0),
(205, '7', 'BCA15226000038', 'Akash', 'akash@gmail.com', '9737184105', '2007-10-10', 'BCA', 5, 'B', 'scrypt:32768:8:1$0zhPt0fsokh4iODu$0397ff31febd762370117dd18ea2264856a2cc65ff310b24d5dcabedf55de8335604539e0635efdb9abf1a0e99c0e506c86f886486be085f26dab1f01585abc3', 'default-avatar.png', 'Active', 0, NULL, '2026-09-26 13:10:16', '2026-09-26 13:10:16', '2024-25', NULL, NULL, 0, NULL, NULL, NULL, NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `student_subjects`
--

DROP TABLE IF EXISTS `student_subjects`;
CREATE TABLE IF NOT EXISTS `student_subjects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `subject_id` int NOT NULL,
  `semester` smallint NOT NULL,
  `academic_year` varchar(20) NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_student_subject_sem_year` (`student_id`,`subject_id`,`semester`,`academic_year`),
  KEY `subject_id` (`subject_id`)
) ENGINE=MyISAM AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `student_subjects`
--

INSERT INTO `student_subjects` (`id`, `student_id`, `subject_id`, `semester`, `academic_year`, `created_at`, `updated_at`) VALUES
(16, 127, 1, 2, '2026-27', '2026-09-13 22:08:44', '2026-09-13 22:08:44'),
(5, 128, 1, 1, '2026-27', '2026-09-13 21:35:43', '2026-09-13 21:35:43'),
(6, 129, 1, 1, '2026-27', '2026-09-13 21:35:43', '2026-09-13 21:35:43'),
(7, 131, 1, 1, '2026-27', '2026-09-13 21:35:43', '2026-09-13 21:35:43'),
(8, 134, 1, 1, '2026-27', '2026-09-13 21:35:43', '2026-09-13 21:35:43'),
(9, 135, 1, 1, '2026-27', '2026-09-13 21:35:43', '2026-09-13 21:35:43'),
(10, 138, 1, 1, '2026-27', '2026-09-13 21:35:43', '2026-09-13 21:35:43'),
(11, 139, 1, 1, '2026-27', '2026-09-13 21:35:43', '2026-09-13 21:35:43'),
(15, 127, 1, 1, '2026-27', '2026-09-13 22:08:44', '2026-09-13 22:08:44'),
(14, 144, 3, 4, '2026-27', '2026-09-13 21:45:03', '2026-09-13 21:45:03'),
(17, 130, 1, 1, '2026-27', '2026-09-13 22:12:32', '2026-09-13 22:12:32'),
(18, 136, 1, 1, '2026-27', '2026-09-13 22:12:32', '2026-09-13 22:12:32'),
(19, 141, 1, 1, '2026-27', '2026-09-13 22:12:32', '2026-09-13 22:12:32'),
(20, 127, 2, 1, '2026-27', '2026-09-13 22:30:59', '2026-09-13 22:30:59'),
(21, 128, 2, 1, '2026-27', '2026-09-13 22:30:59', '2026-09-13 22:30:59'),
(22, 129, 2, 1, '2026-27', '2026-09-13 22:30:59', '2026-09-13 22:30:59'),
(23, 131, 2, 1, '2026-27', '2026-09-13 22:30:59', '2026-09-13 22:30:59'),
(24, 134, 2, 1, '2026-27', '2026-09-13 22:30:59', '2026-09-13 22:30:59'),
(25, 135, 2, 1, '2026-27', '2026-09-13 22:30:59', '2026-09-13 22:30:59'),
(26, 138, 2, 1, '2026-27', '2026-09-13 22:30:59', '2026-09-13 22:30:59'),
(27, 139, 2, 1, '2026-27', '2026-09-13 22:30:59', '2026-09-13 22:30:59');

-- --------------------------------------------------------

--
-- Table structure for table `student_test_answers`
--

DROP TABLE IF EXISTS `student_test_answers`;
CREATE TABLE IF NOT EXISTS `student_test_answers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `attempt_id` int NOT NULL,
  `question_id` int NOT NULL,
  `selected_option` varchar(5) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_correct` tinyint(1) NOT NULL DEFAULT '0',
  `marks_obtained` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_attempt_question` (`attempt_id`,`question_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `student_test_answers`
--

INSERT INTO `student_test_answers` (`id`, `attempt_id`, `question_id`, `selected_option`, `is_correct`, `marks_obtained`) VALUES
(1, 1, 1, 'B', 1, 1),
(2, 1, 2, 'B', 1, 1),
(3, 1, 3, 'D', 1, 1),
(4, 1, 4, 'A', 1, 1),
(5, 1, 5, 'B', 1, 1),
(6, 2, 1, 'C', 0, 0),
(7, 2, 2, 'B', 1, 1),
(8, 2, 3, 'D', 1, 1),
(9, 2, 4, 'A', 1, 1),
(10, 2, 5, 'B', 1, 1),
(11, 3, 6, 'A', 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `student_test_attempts`
--

DROP TABLE IF EXISTS `student_test_attempts`;
CREATE TABLE IF NOT EXISTS `student_test_attempts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_id` int NOT NULL,
  `student_id` int NOT NULL,
  `start_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `submit_time` datetime DEFAULT NULL,
  `time_taken_seconds` int NOT NULL DEFAULT '0',
  `score` float NOT NULL DEFAULT '0',
  `percentage` float NOT NULL DEFAULT '0',
  `tab_switch_count` int NOT NULL DEFAULT '0',
  `status` enum('in_progress','submitted','auto_submitted_cheating','timed_out') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'in_progress',
  `ip_address` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_test_attempt` (`test_id`,`student_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `student_test_attempts`
--

INSERT INTO `student_test_attempts` (`id`, `test_id`, `student_id`, `start_time`, `submit_time`, `time_taken_seconds`, `score`, `percentage`, `tab_switch_count`, `status`, `ip_address`) VALUES
(1, 1, 127, '2026-09-27 05:54:15', '2026-09-27 06:04:15', 600, 5, 100, 1, 'submitted', '127.0.0.1'),
(2, 1, 128, '2026-09-27 05:48:15', '2026-09-27 06:00:15', 720, 4, 80, 1, 'submitted', '127.0.0.1'),
(3, 2, 127, '2026-09-27 06:16:35', '2026-09-27 06:17:17', 41, 1, 100, 0, 'submitted', '127.0.0.1');

-- --------------------------------------------------------

--
-- Table structure for table `subjects`
--

DROP TABLE IF EXISTS `subjects`;
CREATE TABLE IF NOT EXISTS `subjects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subject_code` varchar(20) NOT NULL,
  `subject_name` varchar(150) NOT NULL,
  `course` varchar(50) NOT NULL,
  `semester` smallint NOT NULL,
  `subject_type` enum('Theory','Practical') NOT NULL,
  `credits` int NOT NULL,
  `status` enum('Active','Inactive') NOT NULL,
  `created_at` timestamp NULL DEFAULT NULL,
  `updated_at` timestamp NULL DEFAULT NULL,
  `internal_marks` int NOT NULL DEFAULT '30',
  `external_marks` int NOT NULL DEFAULT '70',
  `total_marks` int NOT NULL DEFAULT '100',
  `component_config` text,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `subjects`
--

INSERT INTO `subjects` (`id`, `subject_code`, `subject_name`, `course`, `semester`, `subject_type`, `credits`, `status`, `created_at`, `updated_at`, `internal_marks`, `external_marks`, `total_marks`, `component_config`) VALUES
(1, 'BCA101', 'Fundamental of Programming Language - C', 'BCA', 1, 'Theory', 4, 'Active', '2026-08-16 15:35:27', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(2, 'BCA101A', 'Database Management System & PC Packages', 'BCA', 1, 'Theory', 4, 'Active', '2026-08-16 15:36:08', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(3, 'BCA401', 'Python Programming', 'BCA', 4, 'Theory', 4, 'Active', '2026-09-11 21:46:11', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(4, 'BCA203', 'Electronic Commerce (E-Commerce)', 'BCA', 2, 'Theory', 4, 'Active', '2026-09-11 21:46:11', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(5, 'BCA501A', 'GUI Programming Using C# .net', 'BCA', 5, 'Theory', 4, 'Active', '2026-09-16 08:07:24', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(6, 'BCA501', 'JAVA Programming', 'BCA', 5, 'Theory', 4, 'Active', '2026-09-17 20:55:44', '2026-09-17 20:55:44', 50, 50, 100, NULL),
(7, 'BCA501B', 'Practical - JAVA Programming', 'BCA', 5, 'Practical', 2, 'Active', '2026-09-17 20:56:39', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(8, 'BCA501C', 'Practical - GUI Programming', 'BCA', 5, 'Practical', 2, 'Active', '2026-09-17 20:57:09', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(9, 'BCA502A', 'Operating System', 'BCA', 5, 'Theory', 4, 'Active', '2026-09-17 21:33:36', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(10, 'BCA102A', 'Practical - MS Office', 'BCA', 1, 'Practical', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(11, 'BCA103', 'Computer Organization', 'BCA', 1, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(12, 'BCA104', 'Communication Skills-I', 'BCA', 1, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(13, 'BCA105', 'Understanding India', 'BCA', 1, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(14, 'BCA106', 'Mathematics - I', 'BCA', 1, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(15, 'BCA201', 'Advance Programming Language - C', 'BCA', 2, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(16, 'BCA201A', 'Internet & Web Designing', 'BCA', 2, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(17, 'BCA202A', 'Practical - Internet & Web Designing', 'BCA', 2, 'Practical', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(18, 'BCA204', 'Communication Skills-II', 'BCA', 2, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(19, 'BCA205', 'Integrated Personality Development Course - I', 'BCA', 2, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(20, 'BCA206', 'Mathematics-II', 'BCA', 2, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(21, 'BCA301', 'Data Structure', 'BCA', 3, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(22, 'BCA301A', 'Relational Database Management System', 'BCA', 3, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(23, 'BCA301C', 'Practical - RDBMS', 'BCA', 3, 'Practical', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(24, 'BCA303', 'Computer Network', 'BCA', 3, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(25, 'BCA304', 'Environmental Science', 'BCA', 3, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(26, 'BCA305', 'Health Education', 'BCA', 3, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(27, 'BCA306', 'Computer Security - I', 'BCA', 3, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(28, 'BCA401A', 'Web Development Using PHP', 'BCA', 4, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(29, 'BCA401C', 'Practical - PHP', 'BCA', 4, 'Practical', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(30, 'BCA402', 'System Analysis and Design', 'BCA', 4, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(31, 'BCA404', 'Personality Development & Reasoning Ability', 'BCA', 4, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(32, 'BCA405', 'Integrated Personality Development Course - II', 'BCA', 4, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(33, 'BCA406', 'Computer Security - II', 'BCA', 4, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(34, 'BCA502', 'Software Engineering', 'BCA', 5, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(35, 'BCA506', 'Project Development', 'BCA', 5, 'Practical', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(36, 'BCA601', 'Advance JAVA Programming', 'BCA', 6, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(37, 'BCA601A', 'Web Development Using Asp.Net', 'BCA', 6, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(38, 'BCA601C', 'Practical - Asp.Net', 'BCA', 6, 'Practical', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(39, 'BCA602', 'Unified Modeling Language (UML)', 'BCA', 6, 'Theory', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL),
(40, 'BCA604', 'Digital Communication and Marketing Skills', 'BCA', 6, 'Theory', 2, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 25, 25, 50, NULL),
(41, 'BCA607', 'Industrial Project', 'BCA', 6, 'Practical', 4, 'Active', '2026-09-17 23:57:22', '2026-09-17 23:57:22', 50, 50, 100, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tests`
--

DROP TABLE IF EXISTS `tests`;
CREATE TABLE IF NOT EXISTS `tests` (
  `id` int NOT NULL AUTO_INCREMENT,
  `faculty_id` int DEFAULT NULL,
  `subject_id` int DEFAULT NULL,
  `semester` smallint NOT NULL,
  `division` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'All',
  `title` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `duration_minutes` int NOT NULL DEFAULT '20',
  `total_marks` float NOT NULL DEFAULT '0',
  `passing_marks` float NOT NULL DEFAULT '0',
  `status` enum('draft','published','completed') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft',
  `pdf_filename` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_faculty` (`faculty_id`),
  KEY `idx_subject_sem` (`subject_id`,`semester`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tests`
--

INSERT INTO `tests` (`id`, `faculty_id`, `subject_id`, `semester`, `division`, `title`, `description`, `duration_minutes`, `total_marks`, `passing_marks`, `status`, `pdf_filename`, `created_at`, `updated_at`) VALUES
(1, 6, 3, 2, 'All', 'Python Unit 1: Core Concepts & Functions', 'Official mid-term online quiz covering Python syntax, data types, functions, exception handling, and memory architecture.', 15, 5, 2, 'published', NULL, '2026-09-27 06:08:15', '2026-09-27 06:08:15'),
(2, 6, NULL, 2, 'A', 'Unit Test Automated Quiz', '', 10, 1, 1, 'published', NULL, '2026-09-27 06:08:33', '2026-09-27 06:08:33');

-- --------------------------------------------------------

--
-- Table structure for table `test_questions`
--

DROP TABLE IF EXISTS `test_questions`;
CREATE TABLE IF NOT EXISTS `test_questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_id` int NOT NULL,
  `question_text` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `options_json` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `correct_option` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `marks` float NOT NULL DEFAULT '1',
  `explanation` text COLLATE utf8mb4_unicode_ci,
  `order_index` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_test_id` (`test_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `test_questions`
--

INSERT INTO `test_questions` (`id`, `test_id`, `question_text`, `options_json`, `correct_option`, `marks`, `explanation`, `order_index`) VALUES
(1, 1, 'Which of the following data structures in Python is ordered, mutable, and allows duplicate elements?', '{\"A\": \"Set\", \"B\": \"List\", \"C\": \"Tuple\", \"D\": \"Dictionary Keys\"}', 'B', 1, 'Lists are ordered, mutable sequences that allow duplicate items, defined using square brackets [].', 0),
(2, 1, 'What is the primary difference between a Shallow Copy and a Deep Copy in Python?', '{\"A\": \"Shallow copy duplicates nested objects recursively; deep copy does not.\", \"B\": \"Deep copy constructs a new compound object and recursively inserts copies of child objects.\", \"C\": \"Shallow copy is immutable, whereas deep copy is always mutable.\", \"D\": \"There is no difference in Python 3.\"}', 'B', 1, 'A deep copy constructs a new compound object and then recursively inserts copies of objects found in the original.', 1),
(3, 1, 'Which block in Python exception handling is guaranteed to execute regardless of whether an exception was raised or handled?', '{\"A\": \"try\", \"B\": \"except\", \"C\": \"else\", \"D\": \"finally\"}', 'D', 1, 'The \'finally\' clause is always executed before leaving the try statement, whether an exception has occurred or not.', 2),
(4, 1, 'What is the average time complexity of key lookup in a Python dictionary?', '{\"A\": \"O(1)\", \"B\": \"O(n)\", \"C\": \"O(log n)\", \"D\": \"O(n^2)\"}', 'A', 1, 'Python dictionaries are hash tables providing average O(1) time complexity for search, insert, and delete operations.', 3),
(5, 1, 'Which built-in Python function returns both the index and value when iterating over a sequence?', '{\"A\": \"range()\", \"B\": \"enumerate()\", \"C\": \"zip()\", \"D\": \"map()\"}', 'B', 1, 'The enumerate() function adds a counter to an iterable and returns it as an enumerate object of (index, item) pairs.', 4),
(6, 2, 'What is Python?', '{\"A\": \"Programming Language\", \"B\": \"Snake\", \"C\": \"Car\", \"D\": \"Food\"}', 'A', 1, 'Python is a high-level interpreted programming language.', 0);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
