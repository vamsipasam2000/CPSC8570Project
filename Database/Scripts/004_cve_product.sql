CREATE TABLE `cve_product` (
  `cve_id` varchar(50) DEFAULT NULL,
  `product` varchar(256) DEFAULT NULL,
  KEY `cve_id` (`cve_id`),
  CONSTRAINT `cve_product_ibfk_1` FOREIGN KEY (`cve_id`) REFERENCES `cve` (`cve_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
