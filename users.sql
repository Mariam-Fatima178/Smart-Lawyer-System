-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 24, 2024 at 05:40 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `user_auth`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`) VALUES
(1, 'mariam@12', '$2b$12$UOoZ2wgPh39cwquonhAc8uq2a5yAWopC8RzIdrmKHQkNAIO6okK/6'),
(2, 'mariam@gmail.com', '$2b$12$zHgfQa109BvbmxAtmCLD0.UrbUFjZSTDPhGHBkSoCLV6ubc.2MvFC'),
(3, 'saria@gmail.com', '$2b$12$1B3W2bk0qcXkUa1RhjQPdeqGi6RkneNohDWzkv5JDvMroiPi1umMC'),
(4, 'anna12@gmail.com', '$2b$12$8OkNsumRW5kHtByvISqTVeM/hwsz3b4p92UpnPK3dDnyGb3UJhny.'),
(5, 'anna127@gmail.com', '$2b$12$jnnLZcGsNW8jLNiC8v7kDe9N3lBv4zsgLj0t01qGR5t81Xh/tlg9.'),
(6, 'zainab@gmail.com', '$2b$12$lYWKpCTurUBHEFcInbPGF.hFA4IqY2ZvQGITPHkv.JqTRBRrSesZ6'),
(7, 'zainab12@gmail.com', '$2b$12$v472fqLTYAeh/lX9GhcTE.Ci39RAPhih2aiGspaqMln5ptbagGVTK'),
(8, 'zainab122@gmail.com', '$2b$12$JxvkFXFn994wJiaOmBbgfudqHhNzzvv.bvZr1IN9mQsdJTR3D20vS'),
(9, 'saria12@gmail.com', '$2b$12$zZlRGawW6v4gPYL5fU/EV.MLD.SuydvZ3RuE6UpcSnS6U0WailpSq'),
(10, 'mariam@gmail.com', '$2b$12$zZlcfSHp7F743J27yxGVwumLBxBR/7aDoFDfdgHM57FsDRaVwK5Qi'),
(11, 'fatima@gmail.com', '$2b$12$uZoIxE2OtAfPe4DDXa9Y2OUs3hp31PctQoIJ9FdR7HxYfR0ph9QVq');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
