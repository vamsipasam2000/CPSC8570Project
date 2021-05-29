from Database.db_repository import DBRepository
from VCCMappings.CommitMappingClass import  CommitMapping
from git import Repo
from warnings import warn

gt_path = '../../Data/GroundTruthMappings/chromium_gt.txt'

repo_path = '/srv/vcc_repos/chromium'
repo = Repo(repo_path)
db = DBRepository()
mappings = []
with open(gt_path, 'r+') as f:

    for data in f.readlines()[1:]:
        if data[0] == '#' or data[0] == '%':
            continue
        splits = data.split("  ")
        cve = splits[2]
        try:
            fix = repo.commit(splits[1])
        except:
            warn(f'Commit not found {splits[1]}')
            continue
        mapping = CommitMapping(fix, 'VulnerabilityHistoryProject')
        mappings.append((mapping, cve))

db = DBRepository()
for mapping in mappings:
    db.save_fixing_commit(mapping[0], mapping[1])