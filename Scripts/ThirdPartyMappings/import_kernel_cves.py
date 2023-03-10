import sys
sys.path.append("/home/manuel.brack/VulnerabilityLifetimes")

import pandas as pd
import numpy as np
from VCCMappings.RepoInspection import RepoMining
import xml.etree.ElementTree as ET

file = './Data/ThirdPartyMappings/kernel_cves.json'

xml = '''<repo>
                <path>/srv/vcc_repos/linux</path>              
            </repo>'''


df = pd.read_json(file, orient='index')

df_temp = df[['breaks', 'fixes']]
df_temp = df_temp.replace("", np.NaN, regex=True)
df_temp['cve'] = df_temp.index

print(df_temp)
print(df_temp.shape[0] - df_temp.breaks.isnull().sum())

mappings = {}
for fix in df_temp.fixes.unique():
    df_fix = df_temp.loc[df_temp.fixes == fix]
    cves = list(df_fix.cve.values)
    mappings[fix] = cves

repo_node = ET.fromstring(xml)
print(len(mappings))
repo = RepoMining(repo_node, True, 'kernel')
repo.map_to_list(mappings, 'UbuntuCVETracker')