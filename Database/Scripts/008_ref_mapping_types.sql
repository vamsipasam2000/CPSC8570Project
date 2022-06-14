CREATE TABLE `ref_mapping_types` (
  `id` varchar(50) NOT NULL,
  `description_english` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

INSERT INTO ref_mapping_types(id, description_english)
VALUES ('', 'Empty entry')
, ('TypeCommonID', 'Mapping obtained by linking a commen identifier (e.g. bug ID)')
, ('TypeCommitSha', 'Commit identifier (sha) referenced in CVE entry')
, ('TypeCVEID', 'CVE ID referenced in Commit message')
, ('DebianSecurityTracker','Mappings from the Debian security tracker project (https://salsa.debian.org/security-tracker-team/security-tracker/-/raw/master/data/CVE/list)')
, ('LinuxKernelCVEs','Mappings as curated from the linux kernel cves project (https://github.com/nluedtke/linux_kernel_cves/tree/master/data)')
, ('ManualInspection','Mappings obtain by manually inspecting previously obtained fixing commits.')
, ('PiantadosiApache','Mappings from Piantadosi et al. paper Fixing of Security Vulnerabilities in Open Source Projects: A Case Study of Apache HTTP Server and Apache Tomcat')
, ('UbuntuCVETracker','manually curated mappings from the Ubuntu CVE Tracker(https://git.launchpad.net/ubuntu-cve-tracker)')
, ('VulnerabilityHistoryProject','manually curated mappings from the vulnerability history poject (https://github.com/VulnerabilityHistoryProject)');
