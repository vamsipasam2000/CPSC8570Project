import pandas as pd
import numpy as np
from tqdm import tqdm
from collections import defaultdict

cat_names = defaultdict(lambda: np.NaN)
cat_names[1] = 'Memory and Resource Management'
cat_names[2] = 'Input Validation and Sanitization'
cat_names[3] = 'Code Development Quality'
cat_names[4] = 'Security Measures'
cat_names[5] = 'Others'
cat_names[6] = 'Concurrency'

def manual_cwe_mappings(cwe: str) -> int:
    """Mapps CWE-ID to a top-level category.
    1 - Memory and Resource Management
    2 - Input Validation and Sanitization
    3 - Code Development Quality
    4 - Security Measures
    5 - Others
    6 - Concurrency
    CWEs that are not included return None, as well as the CWE \'NVD-noinfo\'"""
    mappings = {'20': 2, '189': 4, '119': 1, '125': 1, '399': 1, 'NVD-Other': 5, '200': 4, '476': 1, '264': 4,
                '416': 1, '835': 3, 'NVD-noinfo': np.NaN, '362': 6, '400': 1, '787': 1, '772': 1, '310': 4, '190': 1,
                '74': 2, '17': 3, '284': 4, '415': 1, '369': 3, '19': 5, '834': 3, '79': 4, '754': 5, '674': 3,
                '120': 1, '94': 2, '388': 5, '269': 4, '254': 4, '129': 2, '287': 4, '617': 3, '276': 4, '404': 1,
                '134': 5, '862': 4, '320': 4, '89': 2, '347': 4, '682': 3, '16': 5, '665': 5, '755': 5, '732': 4,
                '311': 4, '770': 1, '252': 5, '534': 5, '704': 5, '22': 2, '532': 5, '193': 3, '843': 5, '391': 5,
                '191': 1, '59': 2, '763': 1, '358': 4, '285': 4, '863': 4, '77': 2, '327': 4, '330': 5, '295': 5,
                '352': 5, '92': 4, '664': 1, '93': 2, '275': 4, '434': 5, '707': 2, '668': 4, '361': 6, '319': 4,
                '255': 4, '824': 1, '1187': 1, '426': 4, '417': 5, '427': 5, '610': 5, '522': 4, '345': 5, '354': 5,
                '91': 2, '918': 5, '922': 4, '706': 5, '538': 4, '290': 4, '601': 4, '346': 5, '502': 2, '1021': 5,
                '78': 2, '199': 5, '829': 5, '281': 4, '203': 4, '401': 1, '908': 1, '667': 1, '209': 4, '88': 2,
                '459': 1, '326': 4, '270': 4, '331': 5, '122': 1, '367': 6, '909': 1, '552': 4, '436': 5, '131': 1,
                '672': 1, '271': 4, '681': 3, '212': 4}
    try:
        return mappings[cwe]
    except:
        print(f'No mapping for CWE-{cwe}')
        return np.NaN


input_data = {
    'chrome': ['../Data/Lifetimes/chrome.csv', '../Data/Lifetimes/GroundTruth/chrome_gt.csv'],
    'ffmpeg': ['../Data/Lifetimes/ffmpeg.csv'],
    'firefox': ['../Data/Lifetimes/firefox.csv'],
    'httpd': ['../Data/Lifetimes/httpd.csv', '../Data/Lifetimes/GroundTruth/httpd_gt.csv'],
    'openssl': ['../Data/Lifetimes/openssl.csv'],
    'php': ['../Data/Lifetimes/php.csv'],
    'postgres': ['../Data/Lifetimes/postgres.csv'],
    'qemu': ['../Data/Lifetimes/qemu.csv'],
    'tcpdump': ['../Data/Lifetimes/tcpdump.csv'],
    'wireshark': ['../Data/Lifetimes/wireshark.csv'],
    'kernel': ['../Data/Lifetimes/kernel.csv', '../Data/Lifetimes/GroundTruth/kernel_gt.csv'],
              }
input_data_li_paxson = {
    'chrome': ['../Data/Lifetimes/chrome_lipaxson.csv', '../Data/Lifetimes/GroundTruth/chrome_gt_lipaxson.csv'],
    'ffmpeg': ['../Data/Lifetimes/ffmpeg_lipaxson.csv'],
    'firefox': ['../Data/Lifetimes/firefox_lipaxson.csv'],
    'httpd': ['../Data/Lifetimes/httpd_lipaxson.csv', '../Data/Lifetimes/GroundTruth/httpd_lipaxson_gt.csv'],
    'openssl': ['../Data/Lifetimes/openssl_lipaxson.csv'],
    #'php': ['../Data/Lifetimes/php.csv'],
    'postgres': ['../Data/Lifetimes/postgres_lipaxson.csv'],
    'qemu': ['../Data/Lifetimes/qemu_lipaxson.csv'],
    'tcpdump': ['../Data/Lifetimes/tcpdump_lipaxson.csv'],
    'wireshark': ['../Data/Lifetimes/wireshark_lipaxson.csv'],
    'kernel': ['../Data/Lifetimes/kernel_lipaxson.csv', '../Data/Lifetimes/GroundTruth/kernel_gt.csv'],
}

input_vccfinder_gt = {
    'chrome': ['../Data/Lifetimes/GroundTruth/chrome_gt_vccfinder.csv'],
    'kernel': ['../Data/Lifetimes/GroundTruth/kernel_gt_vccfinder.csv'],
    'httpd': ['../Data/Lifetimes/GroundTruth/httpd_gt_vccfinder.csv']
}

pickle_path = 'complete_lifetimes_v4.pd'

df_temp = None

for config_code, data in input_data.items():
    df = pd.read_csv(data[0], delimiter=';', parse_dates=['Fixing date', 'VCC-heuristic date', 'VCC-oldest date'
        , 'VCC-newest date', 'Average date', 'Weighted Average date'])
    if 'VCC sha' not in df.columns:
        df['VCC sha'] = np.nan
    if 'VCC date' not in df.columns:
        df['VCC date'] = np.nan

    df['Config_Code'] = config_code

    for data_cndt in data[1:]:
        df_cndt = pd.read_csv(data_cndt, delimiter=';', parse_dates=['Fixing date', 'VCC-heuristic date', 'VCC-oldest date'
            , 'VCC-newest date', 'Average date', 'Weighted Average date'])
        if 'VCC sha' not in df_cndt.columns:
            df_cndt['VCC sha'] = np.nan
        if 'VCC date' not in df_cndt.columns:
            df_cndt['VCC date'] = np.nan

        df_cndt['Config_Code'] = config_code

        df = df.append(df_cndt, ignore_index=True)

    if df_temp is None:
        df_temp = df
    else:
        df_temp = df_temp.append(df, ignore_index=True)
    print(f'Loaded {df.shape[0]} entries for {config_code}')

df_temp['VCC date'] = pd.to_datetime(df_temp['VCC date'], utc=True).astype('datetime64[ns]')
df_temp['Fixing date'] = pd.to_datetime(df_temp['Fixing date'], utc=True).astype('datetime64[ns]')
df_temp['Weighted Average date'] = pd.to_datetime(df_temp['Weighted Average date'], utc=True).astype('datetime64[ns]')
df_temp['VCC-newest date'] = pd.to_datetime(df_temp['VCC-newest date'], utc=True).astype('datetime64[ns]')

df_lp = None

for config_code, data in input_data_li_paxson.items():
    df = pd.read_csv(data[0], delimiter=';', parse_dates=['VCC-newest date'])
    df['Config_Code'] = config_code
    for data_cndt in data[1:]:
        df_cndt = pd.read_csv(data_cndt, delimiter=';', parse_dates=['VCC-newest date'])
        df = df.append(df_cndt, ignore_index=True)
    if df_lp is None:
        df_lp = df
    else:
        df_lp = df_temp.append(df, ignore_index=True)
    print(f'Loaded {df.shape[0]} entries for Li&Paxson heuristic for {config_code}')

df_lp['VCC-newest date'] = pd.to_datetime(df_lp['VCC-newest date'], utc=True).astype('datetime64[ns]')


df_gt_vccfinder = None
for config_code, data in input_vccfinder_gt.items():
    df = pd.read_csv(data[0], delimiter=';', parse_dates=['VCC-heuristic date'])
    df['Config_Code'] = config_code
    for data_cndt in data[1:]:
        df_cndt = pd.read_csv(data_cndt, delimiter=';', parse_dates=['VCC-heuristic date'])
        df = df.append(df_cndt, ignore_index=True)
    if df_gt_vccfinder is None:
        df_gt_vccfinder = df
    else:
        df_gt_vccfinder = df_temp.append(df, ignore_index=True)
    print(f'Loaded {df.shape[0]} entries for VCCFinder GT for {config_code}')

df_gt_vccfinder['VCC-heuristic date'] = pd.to_datetime(df_gt_vccfinder['VCC-heuristic date'], utc=True).astype('datetime64[ns]')

df = pd.DataFrame(columns=['project', 'cve', 'cwe', 'cat', 'cat_name', 'cvss_score', 'stable'
    , 'fix_year', 'latest_fix', 'h_oldest_vcc', 'oldest_vcc', 'lp_vcc', 'vccfinder_vcc',  'lifetime', 'h_lifetime', 'c_lifetime'
    , 'lifetime_lower', 'lp_lifetime', 'vccfinder_lifetime'])


for project in input_data.keys():
    project_df = df_temp.loc[df_temp['Config_Code'] == project]
    project_df_lp = df_lp.loc[df_lp['Config_Code'] == project]
    project_df_vccfinder = df_gt_vccfinder.loc[df_lp['Config_Code'] == project]

    for cve in project_df['CVE'].unique():
        cve_df = project_df.loc[project_df['CVE'] == cve]
        if len(cve_df['CWE'].dropna()) == 0:
            print(project, cve)
            continue
        cwe = list(cve_df['CWE'].dropna())[0]
        cvss_score = list(cve_df['CVSS-Score'])[0]
        stable = list(cve_df['Stable'])[0]

        cat = manual_cwe_mappings(cwe.replace('CWE-', ''))

        latest_fix = cve_df['Fixing date'].max()
        fix_year = latest_fix.year
        h_oldest_vcc = cve_df['Weighted Average date'].min()
        oldest_vcc = cve_df['VCC date'].min()

        lower_bound_vcc = cve_df['VCC-newest date'].min()
        lower_lifetime = (latest_fix - lower_bound_vcc).days

        h_lifetime = (latest_fix - h_oldest_vcc).days

        if oldest_vcc is not np.datetime64('NaT'):
            c_lifetime = (latest_fix - oldest_vcc).days
        else:
            c_lifetime = np.NaN

        if c_lifetime is not np.NaN and c_lifetime > 0:
            lifetime = c_lifetime
        else:
            lifetime = h_lifetime

        if c_lifetime < 0:
            c_lifetime = 0

        if lifetime < 0:
            continue

        cve_lp = project_df_lp.loc[project_df_lp['CVE'] == cve]
        if cve_lp.shape[0] == 0:
            lp_vcc = np.datetime64('NaT')
            lp_lifetime = np.NaN
        else:
            lp_vcc = cve_df['VCC-newest date'].min()
            lp_lifetime = (latest_fix - lp_vcc).days

        cve_vccfinder = project_df_vccfinder.loc[project_df_vccfinder['CVE'] == cve]
        if cve_lp.shape[0] == 0:
            vccfinder_vcc = np.datetime64('NaT')
            vccfinder_lifetime = np.NaN
        else:
            vccfinder_vcc = cve_vccfinder['VCC-heuristic date'].min()
            vccfinder_lifetime = (latest_fix - vccfinder_vcc).days



        row = {'project': project, 'cve': cve, 'cwe': cwe, 'cat': cat, 'cvss_score': cvss_score, 'stable': stable,
               'latest_fix': latest_fix, 'h_oldest_vcc': h_oldest_vcc, 'oldest_vcc': oldest_vcc, 'lp_vcc': lp_vcc,
               'vccfinder_vcc': vccfinder_vcc,
               'lifetime': lifetime , 'h_lifetime': h_lifetime, 'c_lifetime': c_lifetime,
               'lifetime_lower': lower_lifetime, 'lp_lifetime': lp_lifetime, 'vccfinder_lifetime': vccfinder_lifetime,
               'fix_year': fix_year, 'cat_name': cat_names[cat]}

        df = df.append(row, ignore_index=True)

df['project'] = df['project'].astype('category')
df['cwe'] = df['cwe'].astype('category')
df['cat'] = df['cat'].astype('category')
df['cat_name'] = df['cat_name'].astype('category')
df['cvss_score'] = df['cvss_score'].astype('category')
df['stable'].replace('yes', True, inplace=True)
df['stable'].replace('no', False, inplace=True)
df['stable'] = df['stable'].astype('bool')
df['latest_fix'] = df['latest_fix'].astype('datetime64[ns]')
df['fix_year'] = df['fix_year'].astype('int64')
df['h_oldest_vcc'] = df['h_oldest_vcc'].astype('datetime64[ns]')
df['oldest_vcc'] = df['oldest_vcc'].astype('datetime64[ns]')
df['lp_vcc'] = df['lp_vcc'].astype('datetime64[ns]')
df['vccfinder_vcc'] = df['vccfinder_vcc'].astype('datetime64[ns]')
df['lifetime'] = df['lifetime'].astype('int64')
df['h_lifetime'] = df['h_lifetime'].astype('int64')
df['c_lifetime'] = df['c_lifetime'].astype(pd.Int64Dtype())
df['lifetime_lower'] = df['lifetime_lower'].astype('int64')
df['lp_lifetime'] = df['lp_lifetime'].astype('int64')
df['vccfinder_lifetime'] = df['vccfinder_lifetime'].astype('int64')

df.to_pickle(pickle_path)

print(f'Pickle with {df.shape[0]} unique cves accross {len(df["project"].unique())} projects saved to {pickle_path}')
