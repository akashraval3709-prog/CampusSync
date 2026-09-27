-- =======================================================
-- CampusSync - Smart College Management System
-- Database Schema Script (Phase 1)
-- Database Name: campussync
-- =======================================================

-- Step 1: Create Database if it doesn't exist
CREATE DATABASE IF NOT EXISTS `campussync` 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Step 2: Switch to campussync database
USE `campussync`;

-- Step 3: Create 'admins' table
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL, -- Stored as Werkzeug password hash
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) UNIQUE NULL,
    `mobile` VARCHAR(15) NULL,
    `profile_photo` VARCHAR(255) DEFAULT 'default-avatar.png',
    `status` ENUM('Active', 'Inactive') DEFAULT 'Active',
    `last_login` DATETIME NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Step 4: Insert default Admin record with Hashed Password for 'admin'
INSERT INTO `admins` (`username`, `password`, `full_name`, `email`, `status`) 
VALUES ('admin', 'scrypt:32768:8:1$Sjn1cTKDzueJlTAq$2f799d8f5e555ffed2b2eadbd6ca62e736bd1e645029d6fba5457134bfb8fbc24ac1db6a2eb6903905db0fcb6a7bb7dac736f64242b83f23253f052bda444f7e', 'System Administrator', 'admin@campussync.edu', 'Active')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Step 5: Create 'college_settings' table
CREATE TABLE IF NOT EXISTS `college_settings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `college_name` VARCHAR(255) NOT NULL DEFAULT 'CampusSync College',
    `college_short_name` VARCHAR(50) NULL,
    `college_type` VARCHAR(50) NULL DEFAULT 'BCA',
    `logo` VARCHAR(255) DEFAULT 'default-logo.png',
    `address` TEXT NULL,
    `city` VARCHAR(100) NULL,
    `state` VARCHAR(100) NULL,
    `pincode` VARCHAR(10) NULL,
    `phone` VARCHAR(20) NULL,
    `email` VARCHAR(100) NULL,
    `website` VARCHAR(255) NULL,
    `principal_name` VARCHAR(100) NULL,
    `established_year` VARCHAR(10) NULL,
    `description` TEXT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Step 6: Create 'academic_settings' table
CREATE TABLE IF NOT EXISTS `academic_settings` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `academic_year` VARCHAR(20) NOT NULL DEFAULT '2026-27',
    `semester_cycle` ENUM('Odd', 'Even') NOT NULL DEFAULT 'Odd',
    `cycle_start_date` DATE NULL,
    `cycle_end_date` DATE NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Step 7: Create 'subjects' table
CREATE TABLE IF NOT EXISTS `subjects` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `subject_code` VARCHAR(20) NOT NULL,
    `subject_name` VARCHAR(150) NOT NULL,
    `course` VARCHAR(50) NOT NULL DEFAULT 'BCA',
    `semester` TINYINT NOT NULL DEFAULT 1,
    `subject_type` ENUM('Theory', 'Practical') NOT NULL DEFAULT 'Theory',
    `credits` INT NOT NULL DEFAULT 4,
    `internal_marks` INT NOT NULL DEFAULT 30,
    `external_marks` INT NOT NULL DEFAULT 70,
    `total_marks` INT NOT NULL DEFAULT 100,
    `status` ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Step 8: Create 'faculty' table
CREATE TABLE IF NOT EXISTS `faculty` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `faculty_code` VARCHAR(50) NOT NULL UNIQUE,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `mobile` VARCHAR(15) NOT NULL,
    `gender` ENUM('Male', 'Female', 'Other') NULL,
    `dob` DATE NULL,
    `qualification` VARCHAR(150) NULL,
    `designation` VARCHAR(100) NULL,
    `department` VARCHAR(50) NULL,
    `joining_date` DATE NULL,
    `address` TEXT NULL,
    `city` VARCHAR(100) NULL,
    `state` VARCHAR(100) NULL,
    `pincode` VARCHAR(10) NULL,
    `profile_photo` VARCHAR(255) DEFAULT 'default-avatar.png',
    `password` VARCHAR(255) NOT NULL, -- Stored as Werkzeug password hash
    `password_changed` TINYINT(1) NOT NULL DEFAULT 0,
    `status` ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    `last_login` DATETIME NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Step 9: Create 'faculty_subject_assignments' table
CREATE TABLE IF NOT EXISTS `faculty_subject_assignments` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `faculty_id` INT NOT NULL,
    `subject_id` INT NOT NULL,
    `division` VARCHAR(10) NOT NULL DEFAULT 'A',
    `status` ENUM('Active', 'Inactive') NOT NULL DEFAULT 'Active',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_fsa_faculty` FOREIGN KEY (`faculty_id`) REFERENCES `faculty` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_fsa_subject` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE,
    CONSTRAINT `uq_faculty_subject_division` UNIQUE (`faculty_id`, `subject_id`, `division`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;




