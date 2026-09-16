CREATE DATABASE IF NOT EXISTS `laptop_shop_pro` CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `laptop_shop_pro`;

-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: laptop_shop_pro
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `customers`
--

DROP TABLE IF EXISTS `customers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `loyalty_points` int DEFAULT '0',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customers`
--

LOCK TABLES `customers` WRITE;
/*!40000 ALTER TABLE `customers` DISABLE KEYS */;
INSERT INTO `customers` VALUES (1,'Nguyễn Văn An','0901111111',NULL,'HCM',10,'2025-12-18 13:43:10'),(2,'Trần Thị Bình','0902222222',NULL,'HN',5,'2025-12-18 13:43:10'),(3,'Lê Văn Cường','0903333333',NULL,'ĐN',0,'2025-12-18 13:43:10'),(4,'Phạm Thị Dung','0904444444',NULL,'HCM',20,'2025-12-18 13:43:10'),(5,'Hoàng Văn Em','0905555555',NULL,'CT',0,'2025-12-18 13:43:10'),(6,'Đỗ Thị Mai','0906666666',NULL,'HCM',15,'2025-12-18 13:43:10'),(7,'Bùi Văn Hùng','0907777777',NULL,'HN',50,'2025-12-18 13:43:10'),(8,'Vũ Thị Lan','0908888888',NULL,'HP',2,'2025-12-18 13:43:10'),(9,'Đặng Văn Nam','0909999999',NULL,'HCM',100,'2025-12-18 13:43:10'),(10,'Ngô Thị Hoa','0901010101',NULL,'HCM',0,'2025-12-18 13:43:10'),(11,'Trịnh Văn Khôi','0912345678',NULL,'BD',10,'2025-12-18 13:43:10'),(12,'Lý Thị Mận','0987654321',NULL,'LA',5,'2025-12-18 13:43:10'),(13,'Dương Văn Tuấn','0911223344',NULL,'VT',12,'2025-12-18 13:43:10'),(14,'Mai Thị Tuyết','0933445566',NULL,'ĐN',8,'2025-12-18 13:43:10'),(15,'Hồ Văn Hiếu','0977889900',NULL,'HCM',60,'2025-12-18 13:43:10'),(16,'Cao Thị Trang','0966778899',NULL,'HN',4,'2025-12-18 13:43:10'),(17,'Phan Văn Long','0955667788',NULL,'CT',22,'2025-12-18 13:43:10'),(18,'Lương Thị Yến','0944556677',NULL,'BD',0,'2025-12-18 13:43:10'),(19,'Trương Văn Phúc','0999888777',NULL,'HCM',35,'2025-12-18 13:43:10'),(20,'Đinh Thị Thu','0922334455',NULL,'HCM',11,'2025-12-18 13:43:10'),(21,'Nguyễn Đức Thắng','0919191919',NULL,'HN',9,'2025-12-18 13:43:10'),(22,'Trần Thanh Tâm','0938383838',NULL,'HCM',14,'2025-12-18 13:43:10'),(23,'Lê Quang Hải','0947474747',NULL,'ĐN',3,'2025-12-18 13:43:10'),(24,'Phạm Minh Hoàng','0965656565',NULL,'HP',0,'2025-12-18 13:43:10'),(25,'Hoàng Anh Tú','0972727272',NULL,'HCM',25,'2025-12-18 13:43:10'),(26,'Đỗ Bảo Ngọc','0981818181',NULL,'VT',18,'2025-12-18 13:43:10'),(27,'Bùi Thu Hà','0953535353',NULL,'LA',7,'2025-12-18 13:43:10'),(28,'Vũ Minh Đức','0942424242',NULL,'HCM',15,'2025-12-18 13:43:10'),(29,'Đặng Thùy Linh','0931313131',NULL,'BD',0,'2025-12-18 13:43:10'),(30,'Ngô Kiến Huy','0929292929',NULL,'HCM',50,'2025-12-18 13:43:10'),(31,'google','0941241213','','',0,'2025-12-19 03:39:34');
/*!40000 ALTER TABLE `customers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `import_logs`
--

DROP TABLE IF EXISTS `import_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `import_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_id` int DEFAULT NULL,
  `product_name` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `quantity` int NOT NULL,
  `import_price` decimal(15,2) NOT NULL,
  `total_cost` decimal(15,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `import_logs_ibfk_1` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `import_logs`
--

LOCK TABLES `import_logs` WRITE;
/*!40000 ALTER TABLE `import_logs` DISABLE KEYS */;
INSERT INTO `import_logs` VALUES (1,1,'MacBook Air M1 256GB',25,16000000.00,400000000.00,'2025-11-28 13:43:10'),(2,2,'MacBook Pro M2 13 inch',20,25000000.00,500000000.00,'2025-11-19 13:43:10'),(3,3,'MacBook Pro 14 inch M3',10,38000000.00,380000000.00,'2025-11-21 13:43:10'),(4,4,'Dell XPS 13 9315',15,22000000.00,330000000.00,'2025-11-29 13:43:10'),(5,5,'Dell Inspiron 15 3520',55,10000000.00,550000000.00,'2025-12-05 13:43:10'),(6,6,'Dell Alienware m15 R7',8,45000000.00,360000000.00,'2025-12-11 13:43:10'),(7,7,'Asus TUF Gaming F15',30,15000000.00,450000000.00,'2025-11-21 13:43:10'),(8,8,'Asus ROG Strix G16',13,28000000.00,364000000.00,'2025-11-23 13:43:10'),(9,9,'Asus Zenbook 14 OLED',17,19000000.00,323000000.00,'2025-12-01 13:43:10'),(10,10,'HP Pavilion 15',35,11000000.00,385000000.00,'2025-12-11 13:43:10'),(11,11,'HP Envy x360',12,21000000.00,252000000.00,'2025-11-30 13:43:10'),(12,12,'HP Victus 16',20,17000000.00,340000000.00,'2025-12-11 13:43:10'),(13,13,'Lenovo Legion 5',15,23000000.00,345000000.00,'2025-12-06 13:43:10'),(14,14,'Lenovo ThinkPad X1 Carbon',9,35000000.00,315000000.00,'2025-12-08 13:43:10'),(15,15,'Acer Nitro 5 Tiger',25,16500000.00,412500000.00,'2025-12-03 13:43:10'),(16,16,'Acer Swift 3',23,12000000.00,276000000.00,'2025-12-04 13:43:10'),(17,17,'MSI GF63 Thin',27,14000000.00,378000000.00,'2025-11-21 13:43:10'),(18,18,'MSI Katana 15',11,24000000.00,264000000.00,'2025-12-17 13:43:10'),(19,19,'LG Gram 2023 14 inch',10,26000000.00,260000000.00,'2025-12-02 13:43:10'),(20,20,'Surface Pro 9',11,27000000.00,297000000.00,'2025-12-01 13:43:10');
/*!40000 ALTER TABLE `import_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `order_details`
--

DROP TABLE IF EXISTS `order_details`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `order_details` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `price_at_sale` decimal(15,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `order_details_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_details_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `order_details`
--

LOCK TABLES `order_details` WRITE;
/*!40000 ALTER TABLE `order_details` DISABLE KEYS */;
INSERT INTO `order_details` VALUES (1,1,1,1,18500000.00),(2,2,2,1,29000000.00),(3,3,7,1,17900000.00),(4,4,6,1,52000000.00),(5,5,11,1,24500000.00),(6,6,5,1,12500000.00),(7,7,8,1,32500000.00),(8,8,3,1,42000000.00),(9,9,10,1,13500000.00),(10,10,17,1,16500000.00),(11,11,13,1,27000000.00),(12,12,16,1,14900000.00),(13,13,19,1,30000000.00),(14,14,20,1,31500000.00),(15,15,15,1,19500000.00),(16,16,11,1,24500000.00),(17,17,20,1,31500000.00),(18,18,11,1,24500000.00),(19,20,17,1,16500000.00),(20,21,20,1,31500000.00),(21,22,20,1,31500000.00),(22,23,19,1,30000000.00),(23,24,19,1,30000000.00),(24,25,19,1,30000000.00),(25,26,8,1,32500000.00);
/*!40000 ALTER TABLE `order_details` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `customer_id` int DEFAULT NULL,
  `voucher_code` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `total_amount` decimal(15,2) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'Completed',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `customer_id` (`customer_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `orders_ibfk_2` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,2,1,NULL,18500000.00,'2025-12-17 13:43:10','Completed'),(2,2,2,NULL,29000000.00,'2025-12-16 13:43:10','Completed'),(3,1,4,NULL,17900000.00,'2025-12-15 13:43:10','Completed'),(4,2,7,NULL,52000000.00,'2025-12-14 13:43:10','Completed'),(5,2,9,NULL,24500000.00,'2025-12-13 13:43:10','Completed'),(6,1,15,NULL,12500000.00,'2025-12-12 13:43:10','Completed'),(7,2,19,NULL,32500000.00,'2025-12-11 13:43:10','Completed'),(8,2,30,NULL,42000000.00,'2025-12-10 13:43:10','Completed'),(9,1,5,NULL,13500000.00,'2025-12-08 13:43:10','Completed'),(10,2,8,NULL,16500000.00,'2025-12-06 13:43:10','Completed'),(11,1,10,NULL,27000000.00,'2025-12-03 13:43:10','Completed'),(12,2,12,NULL,14900000.00,'2025-11-30 13:43:10','Completed'),(13,2,14,NULL,30000000.00,'2025-11-28 13:43:10','Completed'),(14,1,20,NULL,31500000.00,'2025-11-23 13:43:10','Completed'),(15,2,25,NULL,19500000.00,'2025-11-20 13:43:10','Completed'),(16,1,NULL,NULL,24500000.00,'2025-12-18 14:46:15','Completed'),(17,5,NULL,NULL,31500000.00,'2025-12-19 03:10:33','Completed'),(18,1,NULL,NULL,24500000.00,'2025-12-19 03:26:33','Completed'),(20,1,NULL,'',16500000.00,'2025-12-19 13:11:20','Completed'),(21,5,NULL,'',31500000.00,'2025-12-19 13:12:12','Completed'),(22,5,NULL,'',31500000.00,'2025-12-19 13:28:49','Completed'),(23,2,NULL,'SV',30000000.00,'2025-12-19 13:51:55','Completed'),(24,1,NULL,'SV',29800000.00,'2025-12-19 14:15:24','Completed'),(25,1,NULL,'SV',29800000.00,'2025-12-19 14:16:33','Completed'),(26,1,NULL,'SV',32300000.00,'2025-12-20 12:29:47','Completed');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `brands`
--

DROP TABLE IF EXISTS `brands`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `brands` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `brands` WRITE;
/*!40000 ALTER TABLE `brands` DISABLE KEYS */;
INSERT INTO `brands` VALUES (6,'Acer'),(4,'Apple'),(2,'Asus'),(1,'Dell'),(3,'HP'),(5,'Lenovo'),(8,'LG'),(9,'Microsoft'),(7,'MSI');
/*!40000 ALTER TABLE `brands` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'Gaming'),(4,'Macbook'),(2,'Ultrabook'),(5,'Văn phòng'),(3,'Workstation');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `products`
--

DROP TABLE IF EXISTS `products`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `supplier_id` int DEFAULT NULL,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `category_id` int DEFAULT NULL,
  `brand_id` int DEFAULT NULL,
  `import_price` decimal(15,2) NOT NULL,
  `price` decimal(15,2) NOT NULL,
  `stock_quantity` int DEFAULT '0',
  `spec_cpu` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `spec_ram` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `spec_screen` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `spec_hard_drive` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `spec_gpu` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `spec_weight` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `spec_os` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `is_active` tinyint DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `supplier_id` (`supplier_id`),
  KEY `category_id` (`category_id`),
  KEY `brand_id` (`brand_id`),
  CONSTRAINT `products_ibfk_1` FOREIGN KEY (`supplier_id`) REFERENCES `suppliers` (`id`) ON DELETE SET NULL,
  CONSTRAINT `products_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`) ON DELETE SET NULL,
  CONSTRAINT `products_ibfk_3` FOREIGN KEY (`brand_id`) REFERENCES `brands` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `products`
--

LOCK TABLES `products` WRITE;
/*!40000 ALTER TABLE `products` DISABLE KEYS */;
INSERT INTO `products` VALUES (1,1,'MacBook Air M1 256GB',4,4,16000000.00,18500000.00,20,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(2,1,'MacBook Pro M2 13 inch',4,4,25000000.00,29000000.00,15,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(3,1,'MacBook Pro 14 inch M3',4,4,38000000.00,42000000.00,5,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(4,2,'Dell XPS 13 9315',2,1,22000000.00,26000000.00,10,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(5,2,'Dell Inspiron 15 3520',5,1,10000000.00,12500000.00,50,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(6,2,'Dell Alienware m15 R7',1,1,45000000.00,52000000.00,3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(7,3,'Asus TUF Gaming F15',1,2,15000000.00,17900000.00,25,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(8,3,'Asus ROG Strix G16',1,2,28000000.00,32500000.00,7,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(9,3,'Asus Zenbook 14 OLED',2,2,19000000.00,22900000.00,12,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(10,4,'HP Pavilion 15',5,3,11000000.00,13500000.00,30,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(11,4,'HP Envy x360',2,3,21000000.00,24500000.00,5,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(12,4,'HP Victus 16',1,3,17000000.00,20500000.00,15,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(13,1,'Lenovo Legion 5',1,5,23000000.00,27000000.00,10,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(14,1,'Lenovo ThinkPad X1 Carbon',3,5,35000000.00,41000000.00,4,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(15,2,'Acer Nitro 5 Tiger',1,6,16500000.00,19500000.00,20,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(16,2,'Acer Swift 3',5,6,12000000.00,14900000.00,18,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(17,3,'MSI GF63 Thin',1,7,14000000.00,16500000.00,21,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(18,3,'MSI Katana 15',1,7,24000000.00,28000000.00,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(19,4,'LG Gram 2023 14 inch',2,8,26000000.00,30000000.00,2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1),(20,4,'Surface Pro 9',2,9,27000000.00,31500000.00,3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `products` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `promotions`
--

DROP TABLE IF EXISTS `promotions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `promotions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `discount_value` decimal(15,2) NOT NULL,
  `discount_type` enum('amount','percent') COLLATE utf8mb4_unicode_ci DEFAULT 'amount',
  `min_order_value` decimal(15,2) DEFAULT '0.00',
  `end_date` date DEFAULT NULL,
  `is_active` tinyint DEFAULT '1',
  `min_bill_value` decimal(15,2) DEFAULT '0.00',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `promotions`
--

LOCK TABLES `promotions` WRITE;
/*!40000 ALTER TABLE `promotions` DISABLE KEYS */;
INSERT INTO `promotions` VALUES (1,'SALE500K',500000.00,'amount',0.00,NULL,1,0.00),(2,'TET2024',10.00,'percent',0.00,NULL,1,0.00),(3,'SINHVIEN',5.00,'percent',0.00,NULL,1,0.00),(4,'HELLO',500000.00,'amount',10000000.00,NULL,1,0.00),(5,'TET2025',10.00,'percent',0.00,NULL,1,0.00),(6,'SV',200000.00,'amount',0.00,NULL,1,0.00);
/*!40000 ALTER TABLE `promotions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `suppliers`
--

DROP TABLE IF EXISTS `suppliers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `suppliers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text COLLATE utf8mb4_unicode_ci,
  `is_active` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `suppliers`
--

LOCK TABLES `suppliers` WRITE;
/*!40000 ALTER TABLE `suppliers` DISABLE KEYS */;
INSERT INTO `suppliers` VALUES (1,'FPT Synnex','02811112222',NULL,'Khu CNC Quận 9, TP.HCM',1),(2,'Digiworld','02833334444',NULL,'Quận 3, TP.HCM',1),(3,'Viễn Sơn','02855556666',NULL,'Quận 1, TP.HCM',1),(4,'PSD','02877778888',NULL,'Bình Thạnh, TP.HCM',1),(5,'FPT Trading','0901234567',NULL,'Hà Nội',1),(6,'Digiworld','0909888777',NULL,'TP.HCM',1),(7,'Viễn Sơn','0912345123',NULL,'Đà Nẵng',1),(8,'FPT Trading','0901234567',NULL,'Hà Nội',1),(9,'Digiworld','0909888777',NULL,'TP.HCM',1),(10,'Viễn Sơn','0912345123',NULL,'Đà Nẵng',1),(11,'FPT Trading','0901234567',NULL,'Hà Nội',1),(12,'Digiworld','0909888777',NULL,'TP.HCM',1),(13,'Viễn Sơn','0912345123',NULL,'Đà Nẵng',1);
/*!40000 ALTER TABLE `suppliers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `role` enum('admin','staff','customer') COLLATE utf8mb4_unicode_ci DEFAULT 'customer',
  `is_active` tinyint DEFAULT '1',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','$2b$12$h/SBZzR0Ee77KL2lLLwoIO541BCsctRcGvMB9jmhKL.JrauRTsqUW','Quản Trị Viên','admin',1),(2,'staff','$2b$12$61KDOj5/im7SlnX7lf4VKuYjwVXiH1/rpZQpIZeGIwpFif9rscHpm','Nguyễn Văn Bán','staff',1),(3,'SUTU','1','Đò khờ khạo','staff',1),(4,'khach1','$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWrn3ILAV5Z.zBqB/g/W.W/W.W','Khách Hàng Demo','customer',1),(5,'lose','$2b$12$t/HX0O1W4OA.5hHIThV2ku9DglPU2sphcipVx0qh9UPLLA/FcXTDa','boruto','customer',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-20 20:15:59
