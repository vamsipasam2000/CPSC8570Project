CREATE TABLE `commit` (
  `com_sha` varchar(50) NOT NULL,
  `com_date_commited` datetime DEFAULT NULL,
  `com_author` varchar(256) DEFAULT NULL,
  `com_message` varchar(5000) DEFAULT NULL,
  `com_config_code` varchar(50) NOT NULL,
  PRIMARY KEY (`com_sha`,`com_config_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
