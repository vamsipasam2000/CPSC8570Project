CREATE TABLE `cve_config_code` (
  `cve_id` varchar(50) DEFAULT NULL,
  `config_code` varchar(256) DEFAULT NULL,
  KEY `cve_id` (`cve_id`),
  CONSTRAINT `cve_config_code_ibfk_1` FOREIGN KEY (`cve_id`) REFERENCES `cve` (`cve_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
