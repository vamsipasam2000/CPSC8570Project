import yaml
import glob
for filepath in glob.iglob(r'C:/Users/manue/Desktop/ThesisCode/Code/chromium_vul_cves/*.yml'):
    with open(filepath, 'r') as stream:
        try:
            cve_data = yaml.safe_load(stream)
        except Exception as exc:
            print(exc)
            continue
    if len(cve_data['fixes']) == 0:
        continue
    if len(cve_data['vccs']) == 0:
        continue
    cve = cve_data['CVE']
    try:
        fixing_commits = [x['commit'] for x in cve_data['fixes'] if x['commit'] is not None]
    except:
        try:
            fixing_commits = [x[':commit'] for x in cve_data['fixes'] if x[':commit'] is not None]
        except:
            print(cve_data['fixes'])
    try:
        vccs = [x['commit'] for x in cve_data['vccs'] if x['commit'] is not None]
    except:
        try:
            vccs = [x[':commit'] for x in cve_data['vccs'] if x[':commit'] is not None]
        except:
            print(cve_data['vccs'])

    #print(cve, len(fixing_commits), len(vccs))