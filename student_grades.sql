-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 02, 2024 at 09:16 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `student_grades`
--

-- --------------------------------------------------------

--
-- Table structure for table `courses`
--

CREATE TABLE `courses` (
  `course_code` varchar(20) NOT NULL,
  `course_name` varchar(100) NOT NULL,
  `credit` int(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `courses`
--

INSERT INTO `courses` (`course_code`, `course_name`, `credit`) VALUES
('60 CS 401', 'Advanced web development', 3),
('60 CS 402', 'Database Management System', 3),
('60 CS 403', 'Software Engineering', 3),
('60 CS 4P1', 'Advanced web development laboratory', 2),
('60 CS 4P2', 'Database Management System Laboratory', 2),
('60 EC L01', 'Internet of Things', 3),
('60 IT 002', 'Design And Analysis of Algorithm', 3),
('60 MA 017', 'Discrete Mathematics', 4);

-- --------------------------------------------------------

--
-- Table structure for table `grade_points`
--

CREATE TABLE `grade_points` (
  `grade` varchar(2) NOT NULL,
  `points` int(2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `grade_points`
--

INSERT INTO `grade_points` (`grade`, `points`) VALUES
('A', 8),
('A+', 9),
('B', 6),
('B+', 7),
('C', 4),
('C+', 5),
('O', 10),
('U', 0);

-- --------------------------------------------------------

--
-- Table structure for table `students`
--

CREATE TABLE `students` (
  `register_number` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `students`
--

INSERT INTO `students` (`register_number`, `name`) VALUES
('2214101', 'AbdulArshath A'),
('2214102', 'Abivarman G'),
('2214103', 'Akshaya K'),
('2214104', 'Ajay S'),
('2214105', 'Ajay V'),
('2214107', 'Alyushra A'),
('2214108', 'Amirtha A'),
('2214112', 'Asraf Ahamed A');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `courses`
--
ALTER TABLE `courses`
  ADD PRIMARY KEY (`course_code`);

--
-- Indexes for table `grade_points`
--
ALTER TABLE `grade_points`
  ADD PRIMARY KEY (`grade`);

--
-- Indexes for table `students`
--
ALTER TABLE `students`
  ADD PRIMARY KEY (`register_number`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
