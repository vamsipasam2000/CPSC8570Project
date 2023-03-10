CREATE TABLE `ref_mapping_types` (
  `id` varchar(50) NOT NULL,
  `description_english` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

INSERT INTO ref_mapping_types(id, description_english)
VALUES ('', 'Empty entry')
, ('TypeCommonID', 'Mapping obtained by linking a commen identifier (e.g. bug ID)')
, ('TypeCommitSha', 'Commit identifier (sha) referenced in CVE entry')
, ('TypeCVEID', 'CVE ID referenced in Commit message');