-- phpMyAdmin SQL Dump
-- version 4.9.11
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Mar 09, 2023 at 06:45 AM
-- Server version: 10.3.38-MariaDB
-- PHP Version: 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `gi6uktd_mgh`
--

-- --------------------------------------------------------

--
-- Table structure for table `bankdetails`
--

CREATE TABLE `bankdetails` (
  `id` int(50) NOT NULL,
  `transferdate` text DEFAULT NULL,
  `accounto` varchar(100) DEFAULT NULL,
  `amount` text DEFAULT NULL,
  `accountnumber` text DEFAULT NULL,
  `amountotransfer` varchar(100) DEFAULT NULL,
  `currency` text DEFAULT NULL,
  `currencytype` text DEFAULT NULL,
  `bankname` varchar(100) DEFAULT NULL,
  `sortcode` varchar(50) DEFAULT NULL,
  `iban` text DEFAULT NULL,
  `bic` text DEFAULT NULL,
  `swift` text DEFAULT NULL,
  `tstatus` text DEFAULT NULL,
  `toption` text DEFAULT NULL,
  `accountname` varchar(100) DEFAULT NULL,
  `banklocation` varchar(100) DEFAULT NULL,
  `billingaddress` varchar(100) DEFAULT NULL,
  `country` text DEFAULT NULL,
  `accountype` varchar(100) DEFAULT NULL,
  `accountno` text NOT NULL,
  `bname` text DEFAULT NULL,
  `bemail` text DEFAULT NULL,
  `email` text DEFAULT NULL,
  `bpass` text DEFAULT NULL,
  `paidin` text DEFAULT NULL,
  `active` text DEFAULT NULL,
  `actcode` text DEFAULT NULL,
  `transfer_count` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `contacts`
--

CREATE TABLE `contacts` (
  `id` int(20) NOT NULL,
  `Name` varchar(100) DEFAULT NULL,
  `contactaddress` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telephone` varchar(100) DEFAULT NULL,
  `message` varchar(100) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

-- --------------------------------------------------------

--
-- Table structure for table `userdetails`
--

CREATE TABLE `userdetails` (
  `id` int(20) NOT NULL,
  `accountno` varchar(50) DEFAULT NULL,
  `pin` varchar(50) DEFAULT NULL,
  `accountnumber` varchar(100) DEFAULT NULL,
  `sort` varchar(50) DEFAULT NULL,
  `fullname` varchar(50) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `email` varchar(50) DEFAULT NULL,
  `bemail` text DEFAULT NULL,
  `telephone` varchar(50) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  `accounttype` varchar(100) DEFAULT NULL,
  `currencytype` text DEFAULT NULL,
  `secq` text DEFAULT NULL,
  `qanswer` text DEFAULT NULL,
  `currency` text DEFAULT NULL,
  `accountstatus` text DEFAULT NULL,
  `tstatus` text DEFAULT NULL,
  `toption` text DEFAULT NULL,
  `amount` text DEFAULT NULL,
  `refree1` varchar(50) DEFAULT NULL,
  `refree2` varchar(50) DEFAULT NULL,
  `minimumwage` varchar(50) DEFAULT NULL,
  `contactaddress` varchar(50) DEFAULT NULL,
  `nextkin` varchar(50) DEFAULT NULL,
  `selfdescription` varchar(50) DEFAULT NULL,
  `lastaccountactivitydate` varchar(50) DEFAULT NULL,
  `creditbalance` varchar(50) DEFAULT NULL,
  `depositbalance` varchar(50) DEFAULT NULL,
  `accountbalance` varchar(50) DEFAULT NULL,
  `lastactivity` varchar(50) DEFAULT NULL,
  `messagefrombank` text DEFAULT NULL,
  `currentinterestrate` varchar(50) DEFAULT NULL,
  `paymentcompany` varchar(50) DEFAULT NULL,
  `tac` text DEFAULT NULL,
  `cot` varchar(50) DEFAULT NULL,
  `irc` varchar(50) DEFAULT NULL,
  `coc` varchar(50) DEFAULT NULL,
  `atc` varchar(50) DEFAULT NULL,
  `mlcc` varchar(50) DEFAULT NULL,
  `bankchargesamount` varchar(50) DEFAULT 'member',
  `activationcode` varchar(100) DEFAULT NULL,
  `active` text DEFAULT NULL,
  `actcode` text DEFAULT NULL,
  `transfer_count` int(11) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Dumping data for table `userdetails`
--

INSERT INTO `userdetails` (`id`, `accountno`, `pin`, `accountnumber`, `sort`, `fullname`, `address`, `email`, `bemail`, `telephone`, `state`, `country`, `accounttype`, `currencytype`, `secq`, `qanswer`, `currency`, `accountstatus`, `tstatus`, `toption`, `amount`, `refree1`, `refree2`, `minimumwage`, `contactaddress`, `nextkin`, `selfdescription`, `lastaccountactivitydate`, `creditbalance`, `depositbalance`, `accountbalance`, `lastactivity`, `messagefrombank`, `currentinterestrate`, `paymentcompany`, `tac`, `cot`, `irc`, `coc`, `atc`, `mlcc`, `bankchargesamount`, `activationcode`, `active`, `actcode`, `transfer_count`) VALUES
(1, 'admin', 'iwulKxWp', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'administrator', NULL, NULL, NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bankdetails`
--
ALTER TABLE `bankdetails`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `contacts`
--
ALTER TABLE `contacts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `userdetails`
--
ALTER TABLE `userdetails`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bankdetails`
--
ALTER TABLE `bankdetails`
  MODIFY `id` int(50) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=429;

--
-- AUTO_INCREMENT for table `contacts`
--
ALTER TABLE `contacts`
  MODIFY `id` int(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `userdetails`
--
ALTER TABLE `userdetails`
  MODIFY `id` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=146;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
