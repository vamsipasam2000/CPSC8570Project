import xml.etree.ElementTree as ET
import argparse
import warnings
from VCCMappings.CVESearch import CVESearch
from VCCMappings.RepoInspection import RepoMining


def merge_dols(dol1: dict, dol2: dict) -> dict:
    """Merges to dictionaries into one"""
    result = dict(dol1, **dol2)
    result.update((k, dol1[k] + dol2[k])
                  for k in set(dol1).intersection(dol2))
    return result


def repo_mining(nodes: ET.Element, database: bool, key: str, cves: dict, mapping: str):
    for repo_node_ in nodes.findall('./repo'):
        repo_ = RepoMining(repo_node_, database, key)
        if cves is None:
            if args.maxcount:
                repo_res_ = repo_.inspect_repo(mapping, args.maxcount)
            else:
                repo_res_ = repo_.inspect_repo(mapping)
        else:
            repo_res_ = repo_.map_to_list(cves, mapping)


config_path = 'config.xml'

parser = argparse.ArgumentParser(description='Map CVEs to bug-fixing commits and VCCs')
parser.add_argument('key', help='Product key in the config xml')
parser.add_argument('-c', "--config", type=str, help='Specify different config file')
parser.add_argument('-d', "--database", help='Store results in the DB. Not supported if -r flag is set.'
                    , action="store_true")

group1 = parser.add_mutually_exclusive_group()
group1.add_argument("-n", "--cve", help='Limit to NVD Search', action="store_true")
group1.add_argument("-r", "--repo", help="Limit to Repository Mining", action="store_true")

parser.add_argument("-m", "--max-count", dest='maxcount'
                    , help="Limit the number of searched commits. May only be used with the repo argument"
                    , type=int)

args = parser.parse_args()


if args.maxcount and not args.repo:
    parser.error("The --maxcount argument can only be used with the --repo argument")

product_key = args.key
if args.config:
    config_path = args.config

print('Loading config file...')

xml_root = ET.parse(config_path)

product_node = xml_root.find('.//product[@name=\'{0}\']'.format(product_key))

if product_node is None:
    raise ValueError('Product key \'{0}\' is not supported'.format(product_key))

cve_search = CVESearch(args.database, product_key)

# If NVD is to be searched
if not args.repo:
    # iterate over all mapping types defined in config
    for mapping_node in product_node.findall('./mapping'):
        mapping_type = mapping_node.find('./type/name').text

        # Currently only supports 3 types of mappings
        if mapping_type not in ['TypeCommonID', 'TypeCommitSha', 'TypeCVEID']:
            raise NotImplementedError('mapping type {0} is not supported'.format(mapping_type))

        cve_res = {}
        # Perform NVD Search
        for nvd_node in mapping_node.findall('./nvd'):
            if mapping_type == 'TypeCVEID':
                cve_res = merge_dols(cve_res, cve_search.get_cves(nvd_node))
            else:
                cve_res = merge_dols(cve_res, cve_search.get_cve_mappings(nvd_node))

        # Perform repository mining
        if not args.cve:
            repo_mining(mapping_node, args.database, product_key, cve_res, mapping_type)

# Only perform repo inspection
else:
    for mapping_node in product_node.findall('./mapping'):
        mapping_type = mapping_node.find('./type/name').text

        try:
            repo_mining(mapping_node, False, product_key, None, mapping_type)
        except NotImplementedError:
            warnings.warn('mapping type {0} is not supported and will be skipped'.format(mapping_type))
