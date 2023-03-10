import sys
sys.path.append("/home/manuel.brack/VulnerabilityLifetimes")

from Database.db_repository import DBRepository
from VCCMappings.CommitMappingClass import  CommitMapping
from git import Repo
from warnings import warn
from VCCMappings.RepoInspection import RepoMining
import xml.etree.ElementTree as ET

gt_path = './Data/GroundTruthMappings/httpd_gt.txt'

xml = '''<repo>
                <path>/srv/vcc_repos/httpd</path>
            </repo>'''

mappings = {}
with open(gt_path, 'r+') as f:

    for data in f.readlines()[1:]:
        if data[0] == '#' or data[0] == '%':
            continue
        splits = data.split("  ")
        cve = splits[2].replace('\n', '').replace('\r', '')
        fix = splits[1].replace('\n', '').replace('\r', '')

        if fix in mappings:
            mappings[fix].append(cve)
        else: 
            mappings[fix] = [cve]

repo_node = ET.fromstring(xml)
repo = RepoMining(repo_node, True, 'httpd')
repo.map_to_list(mappings, 'VulnerabilityHistoryProject')
