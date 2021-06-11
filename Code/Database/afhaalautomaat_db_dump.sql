-- MySQL dump 10.18  Distrib 10.3.27-MariaDB, for debian-linux-gnueabihf (armv8l)
--
-- Host: localhost    Database: afhaalautomaat
-- ------------------------------------------------------
-- Server version	10.3.27-MariaDB-0+deb10u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `action`
--

DROP TABLE IF EXISTS `action`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `action` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Description` varchar(45) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `action`
--

LOCK TABLES `action` WRITE;
/*!40000 ALTER TABLE `action` DISABLE KEYS */;
INSERT INTO `action` VALUES (1,'Temperature Measurement'),(2,'Lock Opened'),(3,'Lock Closed'),(4,'Detection'),(5,'Detection Stopped');
/*!40000 ALTER TABLE `action` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device`
--

DROP TABLE IF EXISTS `device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) NOT NULL,
  `DeviceTypeId` int(11) NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `fk_Device_DeviceType1_idx` (`DeviceTypeId`),
  CONSTRAINT `fk_Device_DeviceType1` FOREIGN KEY (`DeviceTypeId`) REFERENCES `devicetype` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device`
--

LOCK TABLES `device` WRITE;
/*!40000 ALTER TABLE `device` DISABLE KEYS */;
INSERT INTO `device` VALUES (1,'Lock 1',1),(2,'Lock 2',1),(3,'Temperature Sensor',2),(4,'Detector',3);
/*!40000 ALTER TABLE `device` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devicetype`
--

DROP TABLE IF EXISTS `devicetype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devicetype` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Description` varchar(45) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devicetype`
--

LOCK TABLES `devicetype` WRITE;
/*!40000 ALTER TABLE `devicetype` DISABLE KEYS */;
INSERT INTO `devicetype` VALUES (1,'Lock'),(2,'Temperature Sensor'),(3,'Detector');
/*!40000 ALTER TABLE `devicetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `history`
--

DROP TABLE IF EXISTS `history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `history` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Timestamp` timestamp NOT NULL DEFAULT current_timestamp(),
  `Value` float DEFAULT NULL,
  `DeviceId` int(11) NOT NULL,
  `ActionId` int(11) NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `fk_History_Action1_idx` (`ActionId`),
  KEY `fk_History_Device1_idx` (`DeviceId`),
  KEY `Timestamp_idx` (`Timestamp`),
  CONSTRAINT `fk_History_Action1` FOREIGN KEY (`ActionId`) REFERENCES `action` (`Id`),
  CONSTRAINT `fk_History_Device1` FOREIGN KEY (`DeviceId`) REFERENCES `device` (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=5640 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `history`
--

LOCK TABLES `history` WRITE;
/*!40000 ALTER TABLE `history` DISABLE KEYS */;
/*!40000 ALTER TABLE `history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `locker`
--

DROP TABLE IF EXISTS `locker`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `locker` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) NOT NULL,
  `Code` int(11) DEFAULT NULL,
  `DeviceId` int(11) NOT NULL,
  `LockerStatusId` int(11) NOT NULL,
  `OrderId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `fk_Locker_Device1_idx` (`DeviceId`),
  KEY `fk_Locker_Order1_idx` (`OrderId`),
  KEY `fk_Locker_LockerStatus1_idx` (`LockerStatusId`),
  CONSTRAINT `fk_Locker_Device1` FOREIGN KEY (`DeviceId`) REFERENCES `device` (`Id`),
  CONSTRAINT `fk_Locker_LockerStatus1` FOREIGN KEY (`LockerStatusId`) REFERENCES `lockerstatus` (`Id`),
  CONSTRAINT `fk_Locker_Order1` FOREIGN KEY (`OrderId`) REFERENCES `order` (`Id`) ON DELETE SET NULL ON UPDATE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `locker`
--

LOCK TABLES `locker` WRITE;
/*!40000 ALTER TABLE `locker` DISABLE KEYS */;
INSERT INTO `locker` VALUES (1,'Locker 1',1234,1,1,NULL),(2,'Locker 2',1234,2,1,NULL);
/*!40000 ALTER TABLE `locker` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lockerstatus`
--

DROP TABLE IF EXISTS `lockerstatus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lockerstatus` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Description` varchar(45) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lockerstatus`
--

LOCK TABLES `lockerstatus` WRITE;
/*!40000 ALTER TABLE `lockerstatus` DISABLE KEYS */;
INSERT INTO `lockerstatus` VALUES (1,'Leeg'),(2,'Wachten op afhalen'),(3,'Afgehaald');
/*!40000 ALTER TABLE `lockerstatus` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order`
--

DROP TABLE IF EXISTS `order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `order` (
  `Id` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(45) NOT NULL,
  `Email` varchar(45) NOT NULL,
  `Tel` varchar(15) DEFAULT NULL,
  `Description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=114 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order`
--

LOCK TABLES `order` WRITE;
/*!40000 ALTER TABLE `order` DISABLE KEYS */;
/*!40000 ALTER TABLE `order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `Username` varchar(45) NOT NULL,
  `Password` varbinary(32) NOT NULL,
  `Salt` varbinary(32) NOT NULL,
  PRIMARY KEY (`Username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-06-11 18:33:38
