import sys
sys.path.append("~/VulnerabilityLifetimes")

from VCCMappings.RepoInspection import RepoMining
import re
import xml.etree.ElementTree as ET

file = './Data/ThirdPartyMappings/DebianSecurityTracker.txt'

xml_wireshark = '''<repo>
                <path>/srv/vcc_repos/wireshark</path>              
            </repo>'''

xml_ffmpeg = '''<repo>
                <path>/srv/vcc_repos/FFmpeg</path>              
            </repo>'''

xml_openssl = '''<repo>
                <path>/srv/vcc_repos/openssl</path>              
            </repo>'''

xml_postgres = '''<repo>
                <path>/srv/vcc_repos/postgres</path>              
            </repo>'''

xml_qemu = '''<repo>
                <path>/srv/vcc_repos/qemu</path>              
            </repo>'''

xml_httpd = '''<repo>
                <path>/srv/vcc_repos/httpd</path>              
            </repo>'''

xml_tcpdump = '''<repo>
                <path>/srv/vcc_repos/tcpdump</path>              
            </repo>'''

cves_ffmpeg = {}
cves_wireshark = {}
cves_openssl = {}
cves_postgres = {}
cves_qemu = {}
cves_httpd = {}
cves_tcpdump = {}


unique_ffmpeg = 0
unique_wireshark = 0
cve = None

if __name__ == '__main__':
    with open(file, 'r+') as f:
        for data in f.readlines():
            if data.startswith('CVE-'):
                search = re.search('CVE-\d{4}-\d{4,7}', data)
                if search:
                    cve = search.group(0)

            elif '://code.wireshark.org/review/gitweb' in data:
                for res in re.finditer(';a=commit(diff)?;h=[^\s]*', data):
                    bug_id = res.group(0).replace(';a=commit;h=', '').replace(';a=commitdiff;h=', '')
                    if bug_id in cves_wireshark:
                        cves_wireshark[bug_id].append(cve)
                    else:
                        cves_wireshark[bug_id] = [cve]

            elif '://github.com/FFmpeg/FFmpeg' in data or '://git.ffmpeg.org/gitweb/ffmpeg.git' in data:
                for res in re.finditer('/commit/[^\s]*', data):
                    bug_id = res.group(0).replace('/commit/', '')
                    if bug_id in cves_ffmpeg:
                        cves_ffmpeg[bug_id].append(cve)
                    else:
                        cves_ffmpeg[bug_id] = [cve]
            elif '://git.openssl.org/?p=openssl.git' in data:
                for res in re.finditer(';a=commit(diff)?;h=[^\s]*', data):
                    bug_id = res.group(0).replace(';a=commit;h=', '').replace(';a=commitdiff;h=', '')
                    if bug_id in cves_openssl:
                        cves_openssl[bug_id].append(cve)
                    else:
                        cves_openssl[bug_id] = [cve]
            elif '://git.postgresql.org/gitweb/?p=postgresql.git' in data:
                for res in re.finditer(';a=commit(diff)?;h=[^\s]*', data):
                    bug_id = res.group(0).replace(';a=commit;h=', '').replace(';a=commitdiff;h=', '')
                    if bug_id in cves_postgres:
                        cves_postgres[bug_id].append(cve)
                    else:
                        cves_postgres[bug_id] = [cve]
            elif '://git.qemu.org/?p=qemu.git' in data:
                for res in re.finditer(';a=commit(diff)?;h=[^\s]*', data):
                    bug_id = res.group(0).replace(';a=commit;h=', '').replace(';a=commitdiff;h=', '')
                    if bug_id in cves_qemu:
                        cves_qemu[bug_id].append(cve)
                    else:
                        cves_qemu[bug_id] = [cve]
            elif '://github.com/apache/httpd' in data:
                for res in re.finditer('/commit/[^\s]*', data):
                    bug_id = res.group(0).replace('/commit/', '')
                    if bug_id in cves_httpd:
                        cves_httpd[bug_id].append(cve)
                    else:
                        cves_httpd[bug_id] = [cve]
            elif '://github.com/the-tcpdump-group/tcpdump' in data:
                for res in re.finditer('/commit/[^\s]*', data):
                    bug_id = res.group(0).replace('/commit/', '')
                    if bug_id in cves_tcpdump:
                        cves_tcpdump[bug_id].append(cve)
                    else:
                        cves_tcpdump[bug_id] = [cve]

    print('ffmpeg')
    repo_node = ET.fromstring(xml_ffmpeg)
    print(len(cves_ffmpeg))
    repo = RepoMining(repo_node, True, 'ffmpeg')
    repo.map_to_list(cves_ffmpeg, 'DebianSecurityTracker')

    print('wireshark')
    repo_node = ET.fromstring(xml_wireshark)
    print(len(cves_wireshark))
    repo = RepoMining(repo_node, True, 'wireshark')
    repo.map_to_list(cves_wireshark, 'DebianSecurityTracker')

    print('openssl')
    repo_node = ET.fromstring(xml_openssl)
    print(len(cves_openssl))
    repo = RepoMining(repo_node, True, 'openssl')
    repo.map_to_list(cves_openssl, 'DebianSecurityTracker')

    print('postgres')
    repo_node = ET.fromstring(xml_postgres)
    print(len(cves_postgres))
    repo = RepoMining(repo_node, True, 'postgres')
    repo.map_to_list(cves_postgres, 'DebianSecurityTracker')

    print('qemu')
    repo_node = ET.fromstring(xml_qemu)
    print(len(cves_qemu))
    repo = RepoMining(repo_node, True, 'qemu')
    repo.map_to_list(cves_qemu, 'DebianSecurityTracker')

    print('httpd')
    repo_node = ET.fromstring(xml_httpd)
    print(len(cves_httpd))
    repo = RepoMining(repo_node, True, 'httpd')
    repo.map_to_list(cves_httpd, 'DebianSecurityTracker')

    print('tcpdump')
    repo_node = ET.fromstring(xml_tcpdump)
    print(len(cves_tcpdump))
    repo = RepoMining(repo_node, True, 'tcpdump')
    repo.map_to_list(cves_tcpdump, 'DebianSecurityTracker')

