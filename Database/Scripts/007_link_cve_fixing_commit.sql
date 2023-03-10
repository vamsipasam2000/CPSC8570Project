CREATE TABLE `link_cve_fixing_commit` (
  `cve_id` varchar(50) DEFAULT NULL,
  `com_sha` varchar(50) DEFAULT NULL,
  `com_config_code` varchar(50) DEFAULT NULL,
  `mapping_type` varchar(50) NOT NULL,
  `manual_delete` int(11) NOT NULL DEFAULT '0',
  KEY `cve_id` (`cve_id`),
  KEY `com_sha` (`com_sha`),
  KEY `FK_link_cve_fixing_commit_ref_mapping_types_mapping_type` (`mapping_type`),
  CONSTRAINT `FK_link_cve_fixing_commit_ref_mapping_types_mapping_type` FOREIGN KEY (`mapping_type`) REFERENCES `ref_mapping_types` (`id`),
  CONSTRAINT `link_cve_fixing_commit_ibfk_1` FOREIGN KEY (`cve_id`) REFERENCES `cve` (`cve_id`),
  CONSTRAINT `link_cve_fixing_commit_ibfk_2` FOREIGN KEY (`com_sha`) REFERENCES `commit` (`com_sha`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
