-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Oct 31, 2025 at 06:33 AM
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
-- Database: `capstone`
--

-- --------------------------------------------------------

--
-- Table structure for table `activity_log`
--

CREATE TABLE `activity_log` (
  `LoginID` int(11) NOT NULL,
  `Timestamp` datetime DEFAULT current_timestamp(),
  `Action` varchar(100) DEFAULT NULL,
  `UserID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `category`
--

CREATE TABLE `category` (
  `CategoryID` int(11) NOT NULL,
  `Category_Name` varchar(50) DEFAULT NULL,
  `Description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `category`
--

INSERT INTO `category` (`CategoryID`, `Category_Name`, `Description`) VALUES
(1, 'Disposable', 'Disposable Vape Products'),
(2, 'Device', 'Refillable Vape Devices'),
(3, 'E Juices', 'Vape Juice');

-- --------------------------------------------------------

--
-- Table structure for table `email`
--

CREATE TABLE `email` (
  `EmailID` int(11) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `UserID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `email`
--

INSERT INTO `email` (`EmailID`, `Email`, `UserID`) VALUES
(1, 'ycotaba25@yahoo.com.ph', 2),
(2, 'delossantosjayrold213@gmail.com', 3),
(3, '12345@jaja', 4),
(4, 'Kurt@gmail.com', 5),
(5, 'kurtcuramen930@gmail.com', 6),
(6, 'sumacab@gmail.com', 7),
(7, 'betlognijayrold@gmail.com', 8),
(8, 'justine123@gmail.com', 9);

-- --------------------------------------------------------

--
-- Table structure for table `order`
--

CREATE TABLE `order` (
  `OrderID` int(11) NOT NULL,
  `Order_Date` date DEFAULT NULL,
  `Order_Status` varchar(50) NOT NULL DEFAULT 'Pending',
  `Pickup_Status` varchar(50) NOT NULL DEFAULT 'Pending',
  `UserID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order`
--

INSERT INTO `order` (`OrderID`, `Order_Date`, `Order_Status`, `Pickup_Status`, `UserID`) VALUES
(1, '2025-08-08', 'Declined', 'Declined', 2),
(2, '2025-08-30', 'Approved', 'Already Picked Up', 2),
(3, '2025-09-10', 'Approved', 'Cancelled', 6),
(4, '2025-09-10', 'Approved', 'Already Picked Up', 7),
(5, '2025-09-11', 'Approved', 'cancelled', 8),
(6, '2025-09-11', 'Approved', 'cancelled', 2),
(7, '2025-09-12', 'Declined', 'cancelled', 9),
(8, '2025-09-20', 'Approved', 'Already Picked Up', 2),
(9, '2025-09-25', 'Approved', 'Already Picked Up', 2),
(10, '2025-09-25', 'Approved', 'Already Picked Up', 2),
(11, '2025-09-25', 'Approved', 'Already Picked Up', 2),
(12, '2025-09-26', 'Approved', 'Already Picked Up', 2),
(13, '2025-10-20', 'Declined', 'Cancelled', 2),
(14, '2025-10-20', 'Declined', 'Cancelled', 2),
(15, '2025-10-20', 'Declined', 'Cancelled', 2),
(16, '2025-10-20', 'Declined', 'Cancelled', 2),
(17, '2025-10-21', 'Declined', 'Cancelled', 2),
(18, '2025-10-25', 'Approved', 'Already Picked Up', 2),
(19, '2025-10-29', 'Approved', 'Already Picked Up', 2),
(20, '2025-10-29', 'Approved', 'Already Picked Up', 2),
(21, '2025-10-29', 'Approved', 'Already Picked Up', 2),
(22, '2025-10-29', 'Approved', 'Already Picked Up', 2),
(23, '2025-10-29', 'Approved', 'Already Picked Up', 2),
(24, '2025-10-31', 'Approved', 'Already Picked Up', 2),
(25, '2025-10-31', 'Declined', 'Cancelled', 2),
(26, '2025-10-31', 'Declined', 'Cancelled', 4),
(27, '2025-10-31', 'Pending', 'Pending', 2);

-- --------------------------------------------------------

--
-- Table structure for table `order_details`
--

CREATE TABLE `order_details` (
  `Order_DetailsID` int(11) NOT NULL,
  `ProductID` int(11) DEFAULT NULL,
  `OrderID` int(11) DEFAULT NULL,
  `Quantity` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `order_details`
--

INSERT INTO `order_details` (`Order_DetailsID`, `ProductID`, `OrderID`, `Quantity`) VALUES
(1, 7, 1, 1),
(2, 3, 2, 1),
(3, 1, 3, 1),
(4, 3, 3, 1),
(5, 1, 4, 1),
(6, 2, 5, 1),
(7, 2, 6, 1),
(8, 2, 6, 1),
(9, 1, 7, 1),
(10, 2, 8, 1),
(11, 6, 9, 1),
(12, 2, 10, 1),
(13, 4, 11, 1),
(14, 6, 12, 1),
(15, 3, 13, 1),
(16, 2, 13, 1),
(17, 3, 13, 1),
(18, 2, 13, 1),
(19, 2, 13, 1),
(20, 2, 13, 1),
(21, 3, 13, 1),
(22, 3, 14, 1),
(23, 3, 15, 1),
(24, 4, 15, 1),
(25, 3, 16, 1),
(26, 2, 17, 1),
(27, 3, 17, 1),
(28, 3, 17, 1),
(29, 2, 17, 1),
(30, 2, 17, 1),
(31, 2, 17, 1),
(32, 2, 17, 1),
(33, 2, 17, 1),
(34, 2, 17, 1),
(35, 3, 17, 1),
(36, 1, 17, 1),
(37, 1, 17, 1),
(38, 1, 17, 1),
(39, 3, 17, 1),
(40, 6, 18, 1),
(41, 10, 19, 2),
(42, 7, 20, 1),
(43, 7, 21, 1),
(44, 10, 22, 1),
(45, 10, 23, 1),
(46, 1, 24, 1),
(47, 1, 25, 1),
(48, 2, 25, 1),
(49, 6, 26, 1),
(50, 7, 27, 1);

-- --------------------------------------------------------

--
-- Table structure for table `password`
--

CREATE TABLE `password` (
  `PasswordID` int(11) NOT NULL,
  `Password` varchar(255) NOT NULL,
  `UserID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `password`
--

INSERT INTO `password` (`PasswordID`, `Password`, `UserID`) VALUES
(1, '123456', 2),
(2, '123456', 3),
(3, '123456', 4),
(4, '123456', 5),
(5, 'brandomasarap', 6),
(6, 'icecreammasarap', 7),
(7, '123456', 8),
(8, '123456', 9);

-- --------------------------------------------------------

--
-- Table structure for table `product`
--

CREATE TABLE `product` (
  `ProductID` int(11) NOT NULL,
  `Product_Name` varchar(100) DEFAULT NULL,
  `Description` text DEFAULT NULL,
  `Price` decimal(10,2) DEFAULT NULL,
  `Stock` int(11) DEFAULT NULL,
  `CategoryID` int(11) DEFAULT NULL,
  `Image_url` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `product`
--

INSERT INTO `product` (`ProductID`, `Product_Name`, `Description`, `Price`, `Stock`, `CategoryID`, `Image_url`) VALUES
(1, 'DEMON VAPE SALT NIC ', 'DEMON VAPE E-Liquid is crafted by a group of passionate liquid artists who are dedicated to creating flavors that will please vapers. Our goal is not only to provide vape products, but also to bring an immersive experience to vapers. Now, with DEMON VAPE E-Liquid, start a new vape journey. On this journey, you will discover all kinds of wonderful tastes and experience unprecedented happiness and satisfaction. Make DEMON VAPE E-Liquid an integral part of your vape world!\r\nSpecification:\r\n50mg \r\n30ml', 400.00, 92, 3, 'https://vapes.ph/wp-content/uploads/2024/01/1704885000359.png'),
(2, 'Frutta Kool', 'Fruita kool E-juice is crafted with a low nicotine level for a smooth vaping experience. Fruita kool E-juice is with a mix ratio of 60 VG to 40 PG, it delivers a perfect balance of vapor production and flavor intensity.\r\nSpecification:\r\n30mg \r\n30ml', 380.00, 145, 3, 'https://vapes.ph/wp-content/uploads/2024/04/4-2.jpg'),
(3, 'Oxva Xlim Go', 'Vape Kit', 1899.00, 98, 2, 'https://vapes.ph/wp-content/uploads/2024/12/oxva-xlim-go-vape-kit-vapesph.jpg'),
(4, 'OXVA XLIM SQ PRO ', 'Vape Kit', 1300.00, 99, 2, 'https://vapes.ph/wp-content/uploads/2024/01/10001-2.jpg'),
(5, 'Vagend NeXlim Pod', 'Vape Kit', 2100.00, 100, 2, 'https://vapes.ph/wp-content/uploads/2024/12/vagend-nexlim-40w-pod-kit-vape.jpg'),
(6, 'Black Elite V1 ', 'Pod Only', 400.00, 97, 1, 'https://vapes.ph/wp-content/uploads/2024/03/428614548_7176165252468211_6258204137381484537_n_upscayl_4x_realesrgan-x4plus.png'),
(7, 'Black Elite V2', 'Pod Only', 500.00, 97, 1, 'https://vapes.ph/wp-content/uploads/2024/12/black-elite-v2-prefilled-vape-vapes.ph_.jpg'),
(8, 'Denkat Mosmo Stick', 'Disposable', 500.00, 100, 1, 'https://vapes.ph/wp-content/uploads/2024/03/432608123_122143579028084310_3297227317989520721_n_upscayl_4x_realesrgan-x4plus.png'),
(9, 'Denkat X Flava Nimmbox', 'Disposable', 500.00, 100, 1, 'https://vapes.ph/wp-content/uploads/2024/04/433436284_416732380938789_3423108931858734390_n_upscayl_1x_realesrgan-x4plus.png'),
(10, 'DenKat x Geek Bar Pro', 'Disposable', 600.00, 96, 1, 'https://vapes.ph/wp-content/uploads/2024/04/3-1.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `role`
--

CREATE TABLE `role` (
  `RoleID` int(11) NOT NULL,
  `Role_Name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `role`
--

INSERT INTO `role` (`RoleID`, `Role_Name`) VALUES
(1, 'Admin'),
(2, 'Customer');

-- --------------------------------------------------------

--
-- Table structure for table `transaction`
--

CREATE TABLE `transaction` (
  `TransactionID` int(11) NOT NULL,
  `Transaction_Date` date DEFAULT NULL,
  `Total_Price` decimal(10,2) DEFAULT NULL,
  `OrderID` int(11) DEFAULT NULL,
  `UserID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transaction`
--

INSERT INTO `transaction` (`TransactionID`, `Transaction_Date`, `Total_Price`, `OrderID`, `UserID`) VALUES
(1, '2025-09-20', 400.00, 4, 7),
(2, '2025-09-25', 400.00, 9, 2),
(3, '2025-09-25', 380.00, 10, 2),
(4, '2025-09-25', 1300.00, 11, 2),
(5, '2025-09-26', 400.00, 12, 2),
(6, '2025-10-25', 400.00, 18, 2),
(7, '2025-10-29', 1200.00, 19, 2),
(8, '2025-10-29', 500.00, 20, 2),
(9, '2025-10-29', 500.00, 21, 2),
(10, '2025-10-29', 600.00, 22, 2),
(11, '2025-10-29', 600.00, 23, 2),
(12, '2025-10-31', 400.00, 24, 2);

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `UserID` int(11) NOT NULL,
  `F_Name` varchar(50) DEFAULT NULL,
  `M_Name` varchar(50) DEFAULT NULL,
  `L_Name` varchar(50) DEFAULT NULL,
  `RoleID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`UserID`, `F_Name`, `M_Name`, `L_Name`, `RoleID`) VALUES
(2, 'jayrold', 'Ronquillo', 'Delos Santos', 2),
(3, 'jayrold', 'Ronquillo', 'Delos Santos', 1),
(4, 'jay', 'j', 'ds', 2),
(5, 'kurt', 'N', 'Curamen', 2),
(6, 'Kurtnijel', 'Corpuz', 'Curamen', 2),
(7, 'Brando', 'M. ', 'Ice cream', 2),
(8, 'jay', 'rold', 'del', 2),
(9, 'justine', 'delos Santos', 'Ronquillo', 2);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `activity_log`
--
ALTER TABLE `activity_log`
  ADD PRIMARY KEY (`LoginID`),
  ADD KEY `UserID` (`UserID`);

--
-- Indexes for table `category`
--
ALTER TABLE `category`
  ADD PRIMARY KEY (`CategoryID`);

--
-- Indexes for table `email`
--
ALTER TABLE `email`
  ADD PRIMARY KEY (`EmailID`),
  ADD KEY `UserID` (`UserID`);

--
-- Indexes for table `order`
--
ALTER TABLE `order`
  ADD PRIMARY KEY (`OrderID`),
  ADD KEY `UserID` (`UserID`);

--
-- Indexes for table `order_details`
--
ALTER TABLE `order_details`
  ADD PRIMARY KEY (`Order_DetailsID`),
  ADD KEY `ProductID` (`ProductID`),
  ADD KEY `OrderID` (`OrderID`);

--
-- Indexes for table `password`
--
ALTER TABLE `password`
  ADD PRIMARY KEY (`PasswordID`),
  ADD KEY `UserID` (`UserID`);

--
-- Indexes for table `product`
--
ALTER TABLE `product`
  ADD PRIMARY KEY (`ProductID`),
  ADD KEY `CategoryID` (`CategoryID`);

--
-- Indexes for table `role`
--
ALTER TABLE `role`
  ADD PRIMARY KEY (`RoleID`);

--
-- Indexes for table `transaction`
--
ALTER TABLE `transaction`
  ADD PRIMARY KEY (`TransactionID`),
  ADD KEY `OrderID` (`OrderID`),
  ADD KEY `UserID` (`UserID`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`UserID`),
  ADD KEY `RoleID` (`RoleID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `activity_log`
--
ALTER TABLE `activity_log`
  MODIFY `LoginID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `category`
--
ALTER TABLE `category`
  MODIFY `CategoryID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `email`
--
ALTER TABLE `email`
  MODIFY `EmailID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `order`
--
ALTER TABLE `order`
  MODIFY `OrderID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `order_details`
--
ALTER TABLE `order_details`
  MODIFY `Order_DetailsID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=51;

--
-- AUTO_INCREMENT for table `password`
--
ALTER TABLE `password`
  MODIFY `PasswordID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `product`
--
ALTER TABLE `product`
  MODIFY `ProductID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `role`
--
ALTER TABLE `role`
  MODIFY `RoleID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `transaction`
--
ALTER TABLE `transaction`
  MODIFY `TransactionID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `UserID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `activity_log`
--
ALTER TABLE `activity_log`
  ADD CONSTRAINT `activity_log_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `user` (`UserID`);

--
-- Constraints for table `email`
--
ALTER TABLE `email`
  ADD CONSTRAINT `email_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `user` (`UserID`);

--
-- Constraints for table `order`
--
ALTER TABLE `order`
  ADD CONSTRAINT `order_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `user` (`UserID`);

--
-- Constraints for table `order_details`
--
ALTER TABLE `order_details`
  ADD CONSTRAINT `order_details_ibfk_1` FOREIGN KEY (`ProductID`) REFERENCES `product` (`ProductID`),
  ADD CONSTRAINT `order_details_ibfk_2` FOREIGN KEY (`OrderID`) REFERENCES `order` (`OrderID`);

--
-- Constraints for table `password`
--
ALTER TABLE `password`
  ADD CONSTRAINT `password_ibfk_1` FOREIGN KEY (`UserID`) REFERENCES `user` (`UserID`);

--
-- Constraints for table `product`
--
ALTER TABLE `product`
  ADD CONSTRAINT `product_ibfk_1` FOREIGN KEY (`CategoryID`) REFERENCES `category` (`CategoryID`);

--
-- Constraints for table `transaction`
--
ALTER TABLE `transaction`
  ADD CONSTRAINT `transaction_ibfk_1` FOREIGN KEY (`OrderID`) REFERENCES `order` (`OrderID`),
  ADD CONSTRAINT `transaction_ibfk_2` FOREIGN KEY (`UserID`) REFERENCES `user` (`UserID`);

--
-- Constraints for table `user`
--
ALTER TABLE `user`
  ADD CONSTRAINT `user_ibfk_1` FOREIGN KEY (`RoleID`) REFERENCES `role` (`RoleID`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
