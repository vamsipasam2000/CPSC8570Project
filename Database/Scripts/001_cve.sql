CREATE TABLE `cve` (
  `cve_id` varchar(50) NOT NULL,
  `cve_date_created` datetime DEFAULT NULL,
  `cve_date_last_modified` datetime DEFAULT NULL,
  `cve_cwe_id` varchar(50) DEFAULT NULL,
  `cve_cvss_score` varchar(10) DEFAULT NULL,
  `cve_cvss_time` datetime DEFAULT NULL,
  `cve_cvss_vector` varchar(100) DEFAULT NULL,
  `cve_summary` varchar(5000) DEFAULT NULL,
  PRIMARY KEY (`cve_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
