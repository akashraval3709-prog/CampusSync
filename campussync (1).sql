-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: Sep 24, 2026 at 09:33 AM
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
(1, '2027-28', 'Odd', '2027-06-15', '2028-04-15', '2026-08-16 15:09:50', '2026-09-24 06:41:30', 70);

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `admins`
--

INSERT INTO `admins` (`id`, `username`, `password`, `full_name`, `email`, `mobile`, `profile_photo`, `status`, `last_login`, `created_at`, `updated_at`) VALUES
(1, 'admin', 'scrypt:32768:8:1$mTT8mRzZi5GbH4Bh$b7fd91d56951ce4c10437f20449dea9d1b0c0d75bf1fbe4c441069220da83a973178581a2bd779c228853114aacf6ef5cbf381be255ff6973fef8dec0a059458', 'Administrator', 'admin@campussync.com', '9876543210', 'admin_1_1787122477.jpeg', 'Active', '2026-09-24 09:07:05', '2026-08-02 08:55:04', '2026-09-24 07:07:05');

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
(7, 'BCA15226000099', 'Rajesh Sharma (Alumni Test)', NULL, 'BCA501', 'Cloud Computing', 5, '2025-26', 42.5, 50, NULL, '2026-09-24 06:05:54'),
(8, 'BCA15226000099', 'Rajesh Sharma (Alumni Test)', NULL, 'BCA502', 'Web Frameworks', 5, '2025-26', 38, 50, NULL, '2026-09-24 06:05:54'),
(9, 'BCA15226000099', 'Rajesh Sharma (Alumni Test)', NULL, 'BCA601', 'Information Security', 6, '2025-26', 45, 50, NULL, '2026-09-24 06:05:54'),
(10, 'BCA15226000099', 'Rajesh Sharma (Alumni Test)', NULL, 'BCA602', 'Project Work & Viva', 6, '2025-26', 48, 50, NULL, '2026-09-24 06:05:54');

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
) ENGINE=MyISAM AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `archived_students`
--

INSERT INTO `archived_students` (`id`, `original_student_id`, `roll_number`, `enrollment_no`, `full_name`, `email`, `mobile`, `dob`, `course`, `final_semester`, `division`, `academic_year`, `profile_photo`, `status`, `archived_at`) VALUES
(13, NULL, '99', 'BCA15226000099', 'Rajesh Sharma (Alumni Test)', 'test.alumni@college.edu', '9876543210', NULL, 'BCA', 6, 'A', '2025-26', 'default-avatar.png', 'Archived', '2026-09-24 06:05:54'),
(14, 143, '1', 'BCA15226000016', 'akash raval', 'akashraval3709@gmail.com', '9328976260', '2006-10-10', 'BCA', 6, 'A', '2024-25', 'default-avatar.png', 'Inactive', '2026-09-24 06:41:29'),
(15, 149, '2', 'BCA15226000020', 'DEVIDKUMAR DANABHAI PARMAR', 'devidparmar8954@gmail.com', '9054702563', '2006-09-17', 'BCA', 6, 'A', '2024-25', 'default-avatar.png', 'Inactive', '2026-09-24 06:41:29'),
(16, 204, '5', 'BCA15226000037', 'Urvi Thakkar', 'urvi.thakkar505@campussync.edu', '9870005005', '2004-07-04', 'BCA', 6, 'A', '2026-27', 'default-avatar.png', 'Inactive', '2026-09-24 06:41:29'),
(17, 203, '4', 'BCA15226000036', 'Nirav Prajapati', 'nirav.prajapati504@campussync.edu', '9870005004', '2003-11-12', 'BCA', 6, 'A', '2026-27', 'default-avatar.png', 'Inactive', '2026-09-24 06:41:29'),
(18, 202, '3', 'BCA15226000035', 'Manan Shukla', 'manan.shukla503@campussync.edu', '9870005003', '2004-03-21', 'BCA', 6, 'A', '2026-27', 'default-avatar.png', 'Inactive', '2026-09-24 06:41:30'),
(19, 201, '2', 'BCA15226000034', 'Hetvi Vora', 'hetvi.vora502@campussync.edu', '9870005002', '2004-10-08', 'BCA', 6, 'A', '2026-27', 'default-avatar.png', 'Inactive', '2026-09-24 06:41:30'),
(20, 200, '1', 'BCA15226000033', 'Chirag Panchal', 'chirag.panchal501@campussync.edu', '9870005001', '2004-05-16', 'BCA', 6, 'A', '2026-27', 'default-avatar.png', 'Inactive', '2026-09-24 06:41:30');

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
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
) ENGINE=MyISAM AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

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
(26, 156, 5, 5, '2026-27', 'A', 5, 1, '2026-09-18 08:55:02', '2026-09-18 08:55:02'),
(27, 156, 8, 5, '2026-27', 'A', 1, 1, '2026-09-18 10:07:17', '2026-09-18 10:07:17'),
(28, 156, 7, 5, '2026-27', 'A', 1, 1, '2026-09-18 10:07:54', '2026-09-18 10:07:54'),
(34, 204, 6, 5, '2026-27', 'A', 5, 1, '2026-09-19 03:56:27', '2026-09-19 03:56:27'),
(35, 203, 6, 5, '2026-27', 'A', 5, 1, '2026-09-19 03:56:27', '2026-09-19 03:56:27'),
(33, 156, 6, 5, '2026-27', 'A', 5, 1, '2026-09-19 03:56:27', '2026-09-19 03:56:27'),
(36, 202, 6, 5, '2026-27', 'A', 5, 1, '2026-09-19 03:56:27', '2026-09-19 03:56:27'),
(37, 201, 6, 5, '2026-27', 'A', 5, 1, '2026-09-19 03:56:27', '2026-09-19 03:56:27'),
(38, 200, 6, 5, '2026-27', 'A', 5, 1, '2026-09-19 03:56:27', '2026-09-19 03:56:27');

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
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `college_settings`
--

INSERT INTO `college_settings` (`id`, `college_name`, `college_short_name`, `logo`, `address`, `city`, `state`, `pincode`, `phone`, `email`, `website`, `principal_name`, `established_year`, `description`, `created_at`, `updated_at`, `college_type`, `college_stamp`, `principal_signature`, `min_overall_attendance`, `min_subject_attendance`, `attendance_warning_threshold`) VALUES
(1, 'CampusSync College', '', 'college_logo_1787122488.png', '', '', '', '', '', '', '', '', '', '', '2026-08-12 06:46:37', '2026-09-18 11:15:37', '', 'college_stamp_1789729887.png', 'principal_sig_1789729887.png', 70, 70, 50);

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
) ENGINE=MyISAM AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `email_logs`
--

INSERT INTO `email_logs` (`id`, `student_id`, `email_type`, `recipient_email`, `status`, `error_message`, `sent_at`, `retry_count`, `created_at`, `updated_at`) VALUES
(1, 143, 'WELCOME', 'akashraval3709@gmail.com', 'SENT', NULL, '2026-09-13 15:23:50', 0, '2026-09-13 09:53:27', '2026-09-13 09:53:50'),
(2, 144, 'WELCOME', 'piyush@gmail.com', 'SENT', NULL, '2026-09-14 03:15:03', 0, '2026-09-13 21:44:43', '2026-09-13 21:45:03'),
(3, 145, 'WELCOME', 'nandni.devloper17@gmail.com', 'SENT', NULL, '2026-09-18 11:16:24', 1, '2026-09-14 04:09:17', '2026-09-18 05:46:24'),
(4, 146, 'WELCOME', 'nandni@gmail.com', 'SENT', NULL, '2026-09-18 11:16:20', 1, '2026-09-14 04:21:10', '2026-09-18 05:46:20'),
(5, 149, 'WELCOME', 'devidparmar8954@gmail.com', 'SENT', NULL, '2026-09-18 11:16:19', 1, '2026-09-16 08:05:36', '2026-09-18 05:46:19'),
(12, 156, 'WELCOME', 'sachin123@gmail.com', 'SENT', NULL, '2026-09-18 13:53:25', 0, '2026-09-18 08:23:03', '2026-09-18 08:23:25');

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `faculty_code` (`faculty_code`),
  UNIQUE KEY `email` (`email`)
) ENGINE=MyISAM AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `faculty`
--

INSERT INTO `faculty` (`id`, `faculty_code`, `full_name`, `email`, `mobile`, `gender`, `dob`, `qualification`, `designation`, `department`, `joining_date`, `address`, `city`, `state`, `pincode`, `profile_photo`, `password`, `password_changed`, `status`, `last_login`, `created_at`, `updated_at`) VALUES
(6, 'FAC001', 'DEVIDKUMAR DANABHAI PARMAR', 'devidparmar8954@gmail.com', '9054702563', 'Male', NULL, 'MCA', 'Assistant Professor', 'BCA', NULL, '', '', '', '', 'faculty_FAC001_1789164034.jpg', 'scrypt:32768:8:1$nyIqavhoWSPF9avd$97d151e803921e66b06b279e60ce0dfbe288d32d2a7120fb0bf575fd7767d8d341746adcaca7429c3ca330a1a25759ca7fb376371de65b19812e10b2b7301181', 1, 'Active', '2026-09-12 04:16:39', '2026-09-11 22:00:35', '2026-09-18 01:30:27'),
(11, 'FAC002', 'RAVAL AKASHBHAI RAMESHBHAI', 'ar3897903@gmail.com', '9328976260', 'Male', NULL, 'MCA', 'Assistant Professor', 'BCA', NULL, '', '', '', '', 'faculty_FAC002_1789168745.jpg', 'scrypt:32768:8:1$YCFsmbzFQAG8M7Ol$e028382a2c9019f74435f2ada138d697c6e2fd8e3b15cffb0a0395381bc73348d0af0c5dad9dabb3d27f726df7d806b3ef738ee011a01cadc69cff7e284f88e2', 1, 'Active', '2026-09-19 09:08:17', '2026-09-11 23:19:06', '2026-09-19 03:38:17'),
(12, 'FAC003', 'piyush', 'piyush@gmail.com', '9904089637', 'Male', '2011-03-16', 'MCA', 'Assistant Professor', 'BCA', '2026-09-18', '', '', '', '', 'default-avatar.png', 'scrypt:32768:8:1$z7cxzZFiBSplKKWa$0a6081eb242da9ba9c2b1d1757962fd4c7c784ae3c32b1b7407d4f9dfef2daf972c8540a2d54a3da99bc15921ec36fbbe0d351415996ce819ea7d741c961b5ab', 1, 'Active', '2026-09-18 17:13:23', '2026-09-18 00:22:34', '2026-09-18 11:43:23');

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
) ENGINE=MyISAM AUTO_INCREMENT=150 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `faculty_subject_assignments`
--

INSERT INTO `faculty_subject_assignments` (`id`, `faculty_id`, `subject_id`, `division`, `status`, `created_at`, `updated_at`) VALUES
(126, 11, 34, 'C', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(143, 6, 1, 'A', 'Active', '2026-09-18 11:37:23', '2026-09-18 11:37:23'),
(118, 11, 7, 'A', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(119, 11, 7, 'B', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(120, 11, 7, 'C', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(121, 11, 8, 'A', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(122, 11, 8, 'B', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(123, 11, 8, 'C', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(124, 11, 34, 'A', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(125, 11, 34, 'B', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(115, 11, 5, 'A', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(116, 11, 5, 'B', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(117, 11, 5, 'C', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(127, 11, 9, 'A', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(128, 11, 9, 'B', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(129, 11, 9, 'C', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(130, 11, 35, 'A', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(131, 11, 35, 'B', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(132, 11, 35, 'C', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(133, 11, 6, 'A', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(134, 11, 6, 'B', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
(135, 11, 6, 'C', 'Active', '2026-09-18 09:59:02', '2026-09-18 09:59:02'),
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
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_lecture_session` (`subject_id`,`semester`,`division`,`academic_year`,`lecture_date`,`lecture_no`),
  KEY `faculty_id` (`faculty_id`)
) ENGINE=MyISAM AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `lecture_attendance_sessions`
--

INSERT INTO `lecture_attendance_sessions` (`id`, `faculty_id`, `subject_id`, `semester`, `division`, `academic_year`, `lecture_date`, `lecture_no`, `status`, `created_at`, `updated_at`) VALUES
(1, 11, 3, 4, 'A', '2026-27', '2026-09-16', 'Lecture 1', 'Draft', '2026-09-16 10:53:52', '2026-09-16 10:53:52'),
(2, 11, 5, 5, 'A', '2026-27', '2026-09-16', 'Lecture 1', 'Draft', '2026-09-16 10:54:44', '2026-09-16 10:55:51'),
(3, 11, 1, 1, 'A', '2026-27', '2026-09-16', 'Lecture 1', 'Submitted', '2026-09-16 10:59:56', '2026-09-16 11:00:10'),
(4, 11, 1, 1, 'B', '2026-27', '2026-09-17', 'Lecture 1', 'Submitted', '2026-09-16 11:03:17', '2026-09-16 11:03:17'),
(5, 11, 5, 5, 'A', '2026-27', '2026-09-17', 'Lecture 1', 'Submitted', '2026-09-16 11:26:27', '2026-09-16 11:26:27'),
(6, 11, 5, 5, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-16 11:27:02', '2026-09-16 11:27:02'),
(7, 11, 5, 5, 'A', '2026-27', '2026-09-19', 'Lecture 1', 'Submitted', '2026-09-16 11:27:24', '2026-09-16 11:27:24'),
(8, 11, 5, 5, 'A', '2026-27', '2026-09-20', 'Lecture 2', 'Submitted', '2026-09-16 11:27:54', '2026-09-16 11:27:54'),
(9, 11, 6, 5, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-18 00:29:05', '2026-09-18 00:29:05'),
(10, 11, 6, 5, 'A', '2026-27', '2026-09-19', 'Lecture 1', 'Submitted', '2026-09-18 00:30:57', '2026-09-18 00:30:57'),
(11, 11, 6, 5, 'A', '2026-27', '2026-09-20', 'Lecture 1', 'Submitted', '2026-09-18 00:32:10', '2026-09-18 00:32:10'),
(12, 11, 6, 5, 'A', '2026-27', '2026-09-21', 'Lecture 1', 'Submitted', '2026-09-18 00:43:39', '2026-09-18 00:43:39'),
(13, 11, 5, 5, 'A', '2026-27', '2026-09-25', 'Lecture 1', 'Submitted', '2026-09-18 08:55:02', '2026-09-18 08:55:02'),
(14, 11, 8, 5, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-18 10:07:17', '2026-09-18 10:07:17'),
(15, 11, 7, 5, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-18 10:07:54', '2026-09-18 10:07:54'),
(16, 12, 2, 1, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-18 11:38:03', '2026-09-18 11:38:03'),
(17, 12, 10, 1, 'A', '2026-27', '2026-09-18', 'Lecture 1', 'Submitted', '2026-09-18 11:38:21', '2026-09-18 11:38:21'),
(18, 12, 10, 1, 'A', '2026-27', '2026-09-19', 'Lecture 1', 'Submitted', '2026-09-18 11:43:49', '2026-09-18 11:43:49'),
(19, 12, 10, 1, 'A', '2026-27', '2026-09-20', 'Lecture 1', 'Submitted', '2026-09-18 11:43:59', '2026-09-18 11:43:59'),
(20, 12, 10, 1, 'A', '2026-27', '2026-09-21', 'Lecture 1', 'Submitted', '2026-09-18 11:44:16', '2026-09-18 11:44:16'),
(21, 12, 10, 1, 'A', '2026-27', '2026-09-22', 'Lecture 1', 'Submitted', '2026-09-18 11:45:19', '2026-09-18 11:45:19'),
(22, 12, 10, 1, 'A', '2026-27', '2026-09-23', 'Lecture 1', 'Submitted', '2026-09-18 11:45:36', '2026-09-18 11:45:36'),
(23, 12, 10, 1, 'A', '2026-27', '2026-09-24', 'Lecture 1', 'Submitted', '2026-09-18 11:45:43', '2026-09-18 11:45:43'),
(24, 11, 6, 5, 'A', '2026-27', '2026-09-23', 'Lecture 1', 'Submitted', '2026-09-19 03:56:27', '2026-09-19 03:56:27');

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_session_student_attendance` (`session_id`,`student_id`),
  KEY `student_id` (`student_id`)
) ENGINE=MyISAM AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `lecture_attendance_students`
--

INSERT INTO `lecture_attendance_students` (`id`, `session_id`, `student_id`, `status`, `created_at`, `updated_at`) VALUES
(1, 1, 144, 'Present', '2026-09-16 10:53:52', '2026-09-16 10:53:52'),
(2, 1, 145, 'Absent', '2026-09-16 10:53:52', '2026-09-16 10:53:52'),
(3, 1, 146, 'Absent', '2026-09-16 10:53:52', '2026-09-16 10:53:52'),
(4, 2, 143, 'Present', '2026-09-16 10:54:44', '2026-09-16 11:25:38'),
(5, 2, 149, 'Absent', '2026-09-16 10:54:44', '2026-09-16 10:54:44'),
(6, 3, 127, 'Absent', '2026-09-16 10:59:56', '2026-09-16 11:00:10'),
(7, 3, 128, 'Present', '2026-09-16 10:59:56', '2026-09-16 10:59:56'),
(8, 3, 129, 'Absent', '2026-09-16 10:59:56', '2026-09-16 11:00:10'),
(9, 3, 131, 'Absent', '2026-09-16 10:59:56', '2026-09-16 11:00:10'),
(10, 3, 134, 'Present', '2026-09-16 10:59:56', '2026-09-16 10:59:56'),
(11, 3, 135, 'Present', '2026-09-16 10:59:56', '2026-09-16 10:59:56'),
(12, 3, 138, 'Absent', '2026-09-16 10:59:56', '2026-09-16 11:00:10'),
(13, 3, 139, 'Present', '2026-09-16 10:59:56', '2026-09-16 10:59:56'),
(14, 4, 132, 'Present', '2026-09-16 11:03:17', '2026-09-16 11:03:17'),
(15, 4, 133, 'Absent', '2026-09-16 11:03:17', '2026-09-16 11:03:17'),
(16, 4, 137, 'Absent', '2026-09-16 11:03:17', '2026-09-16 11:03:17'),
(17, 4, 140, 'Present', '2026-09-16 11:03:17', '2026-09-16 11:03:17'),
(18, 5, 143, 'Present', '2026-09-16 11:26:27', '2026-09-16 11:26:27'),
(19, 5, 149, 'Present', '2026-09-16 11:26:27', '2026-09-16 11:26:27'),
(20, 6, 143, 'Absent', '2026-09-16 11:27:02', '2026-09-16 11:27:02'),
(21, 6, 149, 'Present', '2026-09-16 11:27:02', '2026-09-16 11:27:02'),
(22, 7, 143, 'Present', '2026-09-16 11:27:24', '2026-09-16 11:27:24'),
(23, 7, 149, 'Present', '2026-09-16 11:27:24', '2026-09-16 11:27:24'),
(24, 8, 143, 'Present', '2026-09-16 11:27:54', '2026-09-16 11:27:54'),
(25, 8, 149, 'Present', '2026-09-16 11:27:54', '2026-09-16 11:27:54'),
(26, 9, 143, 'Present', '2026-09-18 00:29:05', '2026-09-18 00:29:05'),
(27, 9, 149, 'Present', '2026-09-18 00:29:05', '2026-09-18 00:29:05'),
(28, 10, 143, 'Present', '2026-09-18 00:30:57', '2026-09-18 00:30:57'),
(29, 10, 149, 'Present', '2026-09-18 00:30:57', '2026-09-18 00:30:57'),
(30, 11, 143, 'Present', '2026-09-18 00:32:10', '2026-09-18 00:32:10'),
(31, 11, 149, 'Present', '2026-09-18 00:32:10', '2026-09-18 00:32:10'),
(32, 12, 143, 'Present', '2026-09-18 00:43:39', '2026-09-18 00:43:39'),
(33, 12, 149, 'Present', '2026-09-18 00:43:39', '2026-09-18 00:43:39'),
(34, 13, 156, 'Present', '2026-09-18 08:55:02', '2026-09-18 08:55:02'),
(35, 14, 156, 'Present', '2026-09-18 10:07:17', '2026-09-18 10:07:17'),
(36, 15, 156, 'Present', '2026-09-18 10:07:54', '2026-09-18 10:07:54'),
(58, 24, 204, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27'),
(57, 24, 203, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27'),
(56, 24, 202, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27'),
(55, 24, 201, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27'),
(54, 24, 200, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27'),
(53, 24, 156, 'Present', '2026-09-19 03:56:27', '2026-09-19 03:56:27');

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
  PRIMARY KEY (`id`),
  UNIQUE KEY `enrollment_no` (`enrollment_no`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `uq_academic_course_sem_roll` (`academic_year`,`course`,`semester`,`roll_number`)
) ENGINE=MyISAM AUTO_INCREMENT=205 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`id`, `roll_number`, `enrollment_no`, `full_name`, `email`, `mobile`, `dob`, `course`, `semester`, `division`, `password`, `profile_photo`, `status`, `password_changed`, `last_login`, `created_at`, `updated_at`, `academic_year`) VALUES
(127, '1', 'BCA15226000001', 'Aarav Patel', 'aarav.patel@college.edu', '9825012345', '2005-05-12', 'BCA', 3, 'A', 'scrypt:32768:8:1$NKUxoUQhJMCsHZgW$7b107b269644e597703f6844a2b760b549f18a1ef79b5a80dc8afca4a0aa899b991a1da8bc8b5bb9c6a79f2c3f27da25ec4676c91c0e6c5b291850f373a83d9f', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:49', '2026-09-24 06:41:30', '2026-27'),
(128, '2', 'BCA15226000002', 'Aditya Vaghela', 'aditya.vaghela@college.edu', '9377122334', '2005-10-02', 'BCA', 3, 'A', 'scrypt:32768:8:1$DnjFUr06xgjjqA5N$ce5bca11cdffa6a97859705a5bee9d48ea7cba38fd76ee3f691ad1b39936d9d2bc25d0773b5d5cff648344434f13c8af16a10cb2de8169119b02fdbe5107e556', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:50', '2026-09-24 06:41:30', '2026-27'),
(129, '3', 'BCA15226000003', 'Bhavya Patel', 'bhavya.patel@college.edu', '9765432109', '2005-12-01', 'BCA', 3, 'A', 'scrypt:32768:8:1$2VRFvG9GgoaivAqv$eb80d89aed60253e2e371ed038a39a1362e8469b6261ec5d99c02dfd18cbe795cec427727e5c01bc9a3b06fa54b7bc0a5be5ca4d9367c1826c8bd94354ff8f66', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:50', '2026-09-24 06:41:30', '2026-27'),
(130, '4', 'BCA15226000004', 'Dev Shah', 'dev.shah@college.edu', '9898765432', '2005-03-30', 'BCA', 3, 'C', 'scrypt:32768:8:1$nDj390rGKqHtFdnW$b2776fff3cdfd8e1f4ae9e4b44e3a3d2308c9e2503cafc3441eb256eebc4eb4090e169df7ba8c426109295aea1a1fee256be44f915f7d47e4530bab1c6cfd020', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:50', '2026-09-24 06:41:30', '2026-27'),
(131, '5', 'BCA15226000005', 'Diya Shah', 'diya.shah@college.edu', '9909988776', '2005-08-22', 'BCA', 3, 'A', 'scrypt:32768:8:1$HbqvOmUE7D0WtRYy$dc9617a31144470ee0786f02b0f39b500f38b262e43a91e016ac680674500ee6ffc1f3001bd51c25dcc5e7e289001914de61c4970f1d1c12aa07b6df8845fa8d', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:50', '2026-09-24 06:41:30', '2026-27'),
(132, '6', 'BCA15226000006', 'Harsh Mehta', 'harsh.mehta@college.edu', '9712345678', '2004-11-05', 'BCA', 3, 'B', 'scrypt:32768:8:1$KHcSGiGLJEh0WYx0$6063458dcf633df3830ff2207cbe3ca6ef5203554a4348af1333bf1efed1e6e3ed6bdca3f97785a4e6eaf80e6b75adbccccc8ecddb5166bd8332ace22d9ab50c', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:51', '2026-09-24 06:41:30', '2026-27'),
(133, '7', 'BCA15226000007', 'Janvi Chawla', 'janvi.chawla@college.edu', '9638055667', '2006-05-17', 'BCA', 3, 'B', 'scrypt:32768:8:1$YSRAlcwaWbNjX10C$e7a847d5b5d6394fc84044a0cfa5ed493a7cfed0e7a515ea946971b43b554a25878d9f5522515318b8f874a6125c647f18aad62d2daf23086be7226c9573c438', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:51', '2026-09-24 06:41:30', '2026-27'),
(134, '8', 'BCA15226000008', 'Karan Rajput', 'karan.rajput@college.edu', '9879011223', '2004-10-28', 'BCA', 3, 'A', 'scrypt:32768:8:1$XrVulzA4ajm56DMY$633306221ac536819afb5b8b37140f7f2f602f4eb49b2a8f99eef132f4482d3d3ac94c398c31d182bd0224a74cfa92265e39143bc4f89723d24752760ccb5d5e', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:51', '2026-09-24 06:41:30', '2026-27'),
(135, '9', 'BCA15226000009', 'Kavya Trivedi', 'kavya.trivedi@college.edu', '9723456789', '2004-09-14', 'BCA', 3, 'A', 'scrypt:32768:8:1$UbJKWbygTxADew2r$d499541af9cafeeefec1fc2128e360986825df9315c7dca5aa6fbe9aab2864acea602a82ee75d44517f11261d039322d8d9526e6a739b99a0621e0ad93e28a69', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:52', '2026-09-24 06:41:30', '2026-27'),
(136, '10', 'BCA15226000010', 'Nidhi Parmar', 'nidhi.parmar@college.edu', '9426033445', '2004-12-08', 'BCA', 3, 'C', 'scrypt:32768:8:1$edxVNydkf6inJvPa$42411800ba20bdb9edc60d3ce453eabe458baacef4dca0f8684e193b4813e813b74a1ccce29d3686f87b550e14a3604bb5deac4a2e42867cbfa54f1bf957d2f6', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:52', '2026-09-24 06:41:30', '2026-27'),
(137, '11', 'BCA15226000011', 'Pooja Dave', 'pooja.dave@college.edu', '9662011223', '2006-01-25', 'BCA', 3, 'B', 'scrypt:32768:8:1$hTuaYKj4O67ooGNe$d2a90923170e5ef3918d2c7667aee4b131b34dae2b6d12ab13cfd23947a1f332ff5b7b0e9d002a7055eb87f35d1cf993db73404934d935a4602a6ab82749f135', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:52', '2026-09-24 06:41:30', '2026-27'),
(138, '12', 'BCA15226000012', 'Riya Sharma', 'riya.sharma@college.edu', '9876543210', '2006-02-18', 'BCA', 3, 'A', 'scrypt:32768:8:1$SmERAQldvJ2YmoGQ$9563cd8d69ec6c9001a137e78cf45a42db9afe0188948e81a6b2912e24917f7bacb1235b35100fb0012c5a7cacb9f2b4d397e62623b11852b9dee9b3e4d4a19f', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:52', '2026-09-24 06:41:30', '2026-27'),
(139, '13', 'BCA15226000013', 'Rohan Joshi', 'rohan.joshi@college.edu', '9558877665', '2005-07-19', 'BCA', 3, 'A', 'scrypt:32768:8:1$5FaxpS0acS1Gtc30$59b5d2fd56d70f949644b4b008c774bdafa40f46cbba37d1f86ebf38fde84cdf9a286a3e10234dff0dd04a58b5876c08962fd3a1fa5a7d9a0e569b381b655942', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:53', '2026-09-24 06:41:30', '2026-27'),
(140, '14', 'BCA15226000014', 'Siddharth Desai', 'siddharth.desai@college.edu', '9106055443', '2006-04-11', 'BCA', 3, 'B', 'scrypt:32768:8:1$IxSYCMRmJSbhVdiQ$ce4cd315d8697512ac87fd7adc1cafd822094133c1224f6c67e8a7dcd6de34bf40bbbbc1b0026678bdd565e4bcca9c555cfb79323e4010e6dc41f8582dee9dd8', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:53', '2026-09-24 06:41:30', '2026-27'),
(141, '15', 'BCA15226000015', 'Tanvi Solanki', 'tanvi.solanki@college.edu', '9998877661', '2005-06-15', 'BCA', 3, 'C', 'scrypt:32768:8:1$AaedyGeyz8mEqntC$68de85f0ab98378c990cbbe64e36f13955f7346b3143b8274a1f5acf948660c8da1885d9915d9b22618659341758b1ecbb5e21fe4bea6a182adcbe61954449b9', 'default-avatar.png', 'Active', 0, NULL, '2026-08-16 04:26:54', '2026-09-24 06:41:30', '2026-27'),
(143, '1', 'BCA15226000016', 'akash raval', 'akashraval3709@gmail.com', '9328976260', '2006-10-10', 'BCA', 6, 'A', 'scrypt:32768:8:1$qvABZku1NVI4oW75$1c57051868b0f3cda982f8815ccaff8b20382e85d5a70eb491b74524a2638919c4f8b4354072d01477ea75dadd1523e3faf8676167b8edbc89bd90c066f24424', 'default-avatar.png', 'Inactive', 0, '2026-09-19 02:14:27', '2026-09-13 09:53:27', '2026-09-24 06:41:29', '2024-25'),
(144, '1', 'BCA15226000017', 'piyush', 'piyush@gmail.com', '9904089637', '2011-03-16', 'BCA', 5, 'A', 'scrypt:32768:8:1$lNW6qqQVfrysUuKt$58bcd44d1cf63aaebbc554672e1da1ae8d14f64b90d0f00e57c353cf3bddf680f19dc5a58259e550b6d8a844a6919d09a0053f54c448b4358340482c87d2fade', 'default-avatar.png', 'Active', 0, NULL, '2026-09-13 21:44:43', '2026-09-24 06:41:30', '2025-26'),
(145, '2', 'BCA15226000018', 'akash r', 'nandni.devloper17@gmail.com', '9328322901', '2001-06-05', 'BCA', 5, 'A', 'scrypt:32768:8:1$HwaR1pGXGuxuTY0M$3466ada68dc2990427f3dd7f5d857164a4aa5cd5aadba8bb0f40438fbc6f644e37cb42e34b005c2ee045c8ec500d79aebe6d5f4eb92a3f9a026c61962578cf87', 'default-avatar.png', 'Active', 0, '2026-09-14 09:40:39', '2026-09-14 04:09:17', '2026-09-24 06:41:30', '2025-26'),
(146, '3', 'BCA15226000019', 'akash r', 'nandni@gmail.com', '9328322902', '2001-06-05', 'BCA', 5, 'A', 'scrypt:32768:8:1$EJrZuTyzVELMnvPY$c5daf3d539468535418f7fcb2dc9db06c2a0901d227e17ea51207fa5d95fcf257bb471c28d235f206720007bd220ab5a71b0ee3da5d0a208c9cabf9043103cdc', 'default-avatar.png', 'Active', 0, NULL, '2026-09-14 04:21:10', '2026-09-24 06:41:30', '2025-26'),
(149, '2', 'BCA15226000020', 'DEVIDKUMAR DANABHAI PARMAR', 'devidparmar8954@gmail.com', '9054702563', '2006-09-17', 'BCA', 6, 'A', 'scrypt:32768:8:1$ZOd1XKntwVL6gacB$a50b526198f91a303404201c3d6e24ecde599aa8b40a180512c2c003c75d0c7ac0866600a7d3031e62e3eae585f1163a7be21a91e5b6c692d7184800791a6b80', 'default-avatar.png', 'Inactive', 0, NULL, '2026-09-16 08:05:36', '2026-09-24 06:41:29', '2024-25'),
(156, '1', 'BCA15226000023', 'Sachin Rathod', 'sachin123@gmail.com', '8980870263', '2005-08-01', 'BCA', 5, 'A', 'scrypt:32768:8:1$RUtZFi9ahMsWebkh$1965365c1cd2f0e9314b8150eefd67ffb2b57764846710382419403d9c414c01d23e29f77ac499335a2e0cc92ab10d45407626f70e975721d0034c9c7b258ea2', 'default-avatar.png', 'Active', 0, '2026-09-19 09:08:38', '2026-09-18 08:23:03', '2026-09-19 03:38:38', '2024-25'),
(204, '5', 'BCA15226000037', 'Urvi Thakkar', 'urvi.thakkar505@campussync.edu', '9870005005', '2004-07-04', 'BCA', 6, 'A', 'scrypt:32768:8:1$LllrtDoLND7qf6rG$252d3372915c2677b4b64b72f8ca812b7e2b87cd050da90a7b1c2e2ad4ef0ba77cede4569c30fda1f3d54554e47046a9f0fd6c2e348849822eca44559cd19a39', 'default-avatar.png', 'Inactive', 0, NULL, '2026-09-19 02:15:55', '2026-09-24 06:41:29', '2026-27'),
(203, '4', 'BCA15226000036', 'Nirav Prajapati', 'nirav.prajapati504@campussync.edu', '9870005004', '2003-11-12', 'BCA', 6, 'A', 'scrypt:32768:8:1$51vLajAmXhrRkab9$e35c743e4b2fc824c45e33dea0e62330d9b053ea5d3834b09431690ac0d6656f26870890b6e22bec0259af880eba65d24357a8a4776e6c1b578f1cfd55bd35b8', 'default-avatar.png', 'Inactive', 0, NULL, '2026-09-19 02:15:55', '2026-09-24 06:41:30', '2026-27'),
(202, '3', 'BCA15226000035', 'Manan Shukla', 'manan.shukla503@campussync.edu', '9870005003', '2004-03-21', 'BCA', 6, 'A', 'scrypt:32768:8:1$kHuTPd97nGUNZnXj$40a1b0d72edc4d5a2b4757aa9ff736ab88300cb74c7df8fecc5c7bf2bd7a044e5b4367dad54dd21017f1a67351b5d56ce2cd1a9e4a6dc116bd074d87de961ce6', 'default-avatar.png', 'Inactive', 0, NULL, '2026-09-19 02:15:54', '2026-09-24 06:41:30', '2026-27'),
(201, '2', 'BCA15226000034', 'Hetvi Vora', 'hetvi.vora502@campussync.edu', '9870005002', '2004-10-08', 'BCA', 6, 'A', 'scrypt:32768:8:1$wAFsrxbav0TmZnvB$e2b61de283b40d2bcc14a84a9cc3adef39e5f43c1518f463c48a0e192be23105fa794ca6a14172591095537a762ce56972bf2f50ad95c6c23c39a29c94b8777e', 'default-avatar.png', 'Inactive', 0, NULL, '2026-09-19 02:15:54', '2026-09-24 06:41:30', '2026-27'),
(200, '1', 'BCA15226000033', 'Chirag Panchal', 'chirag.panchal501@campussync.edu', '9870005001', '2004-05-16', 'BCA', 6, 'A', 'scrypt:32768:8:1$0x0k70khqKhM47GE$2a635adcae77f2f7667a94013afba0f1dabbd80ae2456093be5e36272744cd750f9eccbe29b96053299556cc5cee6cb8fc6f69356855b3e2f5831849c019fbcd', 'default-avatar.png', 'Inactive', 0, '2026-09-19 07:46:12', '2026-09-19 02:15:54', '2026-09-24 06:41:30', '2026-27'),
(199, '5', 'BCA15226000032', 'Yash Barot', 'yash.barot305@campussync.edu', '9870003005', '2005-06-19', 'BCA', 5, 'A', 'scrypt:32768:8:1$H6l3CbJPRRnyckgl$6c2d007015beb89f76120840bcebf5af17f0c868d1d2c673eb0b774e431ad80cc256205e0d9852c6e653cbb8422cb206f1efd281b39924802a84f3e60e3ef6ec', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-24 06:41:30', '2026-27'),
(198, '4', 'BCA15226000031', 'Prachi Soni', 'prachi.soni304@campussync.edu', '9870003004', '2004-12-25', 'BCA', 5, 'A', 'scrypt:32768:8:1$9VwCATxuOLXqBnVx$c204ae379aeac08fd1b436e060ddd842f1a34fee51372739b78370dbd1fe83d010f4dbc37dbc047cc17117dbe8b21b596cf6ea71db31dc592847cc5e8ad18693', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-24 06:41:30', '2026-27'),
(197, '3', 'BCA15226000030', 'Mihir Dave', 'mihir.dave303@campussync.edu', '9870003003', '2005-02-14', 'BCA', 5, 'A', 'scrypt:32768:8:1$9CmsJ80eev8z6VDF$a90ecb419ea95343c967161d097052604dd3197c8a6c408a01640e189eabc07bdb1a66ff3056023f0136947457daefa23094d104d265a6b16aa6fa389732e011', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-24 06:41:30', '2026-27'),
(196, '2', 'BCA15226000029', 'Kiran Zala', 'kiran.zala302@campussync.edu', '9870003002', '2005-08-30', 'BCA', 5, 'A', 'scrypt:32768:8:1$r8iYfu6bDMT6dgaD$0c6a7e28336cbcb1837d3910d691505a4189cd567a407423d5f69af774390bdb6b4e350402340a4290498138fe87a73f635b6b87d01a904d9ea8ac93f6c95a0e', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-24 06:41:30', '2026-27'),
(195, '1', 'BCA15226000028', 'Devansh Pandya', 'devansh.pandya301@campussync.edu', '9870003001', '2005-04-12', 'BCA', 5, 'A', 'scrypt:32768:8:1$peXk4JuUtkEl4X7c$5042a5e6c0812cd9e99cecae835b032d76e7f1ce33624d1f0f03141efd22a547021e3cfad917798a5702a2490464e9f9d2fd04a5f13e4e3e6e824fe10eb41734', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-24 06:41:30', '2026-27'),
(194, '20', 'BCA15226000027', 'Pooja Rathod', 'pooja.rathod105@campussync.edu', '9870001005', '2006-09-18', 'BCA', 3, 'A', 'scrypt:32768:8:1$PyeSN1ppbOLJTCe6$a7cb96b6cca32ad846f6aa5f736981679b28261ac22099f5ed895ac5f27050943a0ea333ab6234657be1fbb93a4b37f6a474c149671c1ae0da95f0ad4e2f053c', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:54', '2026-09-24 06:41:30', '2026-27'),
(193, '19', 'BCA15226000026', 'Meet Shah', 'meet.shah104@campussync.edu', '9870001004', '2005-11-05', 'BCA', 3, 'A', 'scrypt:32768:8:1$ldj8H3FIgZR836E1$df57a0604c1470b6778ba2c82edce477d7ce1110934c69d82ed112705c8359e26ba84bfd5d1caf8a704473064308fa6d848a79c08fa0cb7a41fa3d8cf5d6ce01', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:53', '2026-09-24 06:41:30', '2026-27'),
(192, '18', 'BCA15226000025', 'Khushi Patel', 'khushi.patel103@campussync.edu', '9870001003', '2006-01-10', 'BCA', 3, 'A', 'scrypt:32768:8:1$0Nk1zI9TYsMCKTYy$a6bc028cfe2a5d46b01a36a2ca9d7a2a437a174addaa09c234076d75e98948fc6cc28b3ed32b144631484ae7763ef58a5f6226beaad5d61f7286839843be812e', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:53', '2026-09-24 06:41:30', '2026-27'),
(191, '17', 'BCA15226000024', 'Dhruv Mehta', 'dhruv.mehta102@campussync.edu', '9870001002', '2006-07-22', 'BCA', 3, 'A', 'scrypt:32768:8:1$cWBaP0PeKs5tjqxY$fb8291fb79c930e76fc06fa0d97c9558243050bc018c9b8970b06d2a439a88e96f9dded8579cbdb3c2d9c7164f6e034eba37173823ca8bf3cb99f009f23c37db', 'default-avatar.png', 'Active', 0, NULL, '2026-09-19 02:15:53', '2026-09-24 06:41:30', '2026-27'),
(190, '16', 'BCA15226000022', 'Aayush Joshi', 'aayush.joshi101@campussync.edu', '9870001001', '2006-03-15', 'BCA', 3, 'A', 'scrypt:32768:8:1$3IurQynzm9kaJKOp$1843cf3023fbd7c60badbe1499e70917f91e276b6b359cbc09063f7f6845a5d017fa987863af86c68136422f7950e54082f94b2ff63173f06f37b1437a5a2c1a', 'default-avatar.png', 'Active', 0, '2026-09-19 07:46:12', '2026-09-19 02:15:53', '2026-09-24 06:41:30', '2026-27');

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
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
