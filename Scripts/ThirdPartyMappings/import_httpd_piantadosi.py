import sys
sys.path.append("/home/manuel.brack/VulnerabilityLifetimes")


import pandas as pd
from VCCMappings.RepoInspection import RepoMining
import xml.etree.ElementTree as ET

file = '../../Data/ThirdPartyMappings/http_commits.csv'

xml = '''<repo>
                <path>/srv/vcc_repos/httpd</path>              
            </repo>'''


if __name__ == '__main__':

    df = pd.read_csv(file)
    df_mappings = df[['cve_id', 'fix_commit_id']]

    del df

    mappings = {}
    for fix in df_mappings.fix_commit_id.unique():
        df_fix = df_mappings.loc[df_mappings.fix_commit_id == fix]
        cves = list(df_fix.cve_id.values)
        mappings[fix] = cves

    repo_node = ET.fromstring(xml)
    print(len(mappings))
    repo = RepoMining(repo_node, True, 'httpd')
    repo.map_to_list(mappings, 'PiantadosiApache')