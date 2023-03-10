import argparse
import warnings
import xml.etree.ElementTree as ET
from git import Repo, Commit, BadName
import os
from Heuristics.VuldiggerHeuristic2 import VuldiggerHeuristic2
from Heuristics.VuldiggerHeuristic import VuldiggerHeuristic
from Heuristics.VccfinderHeuristicSerial import VccfinderHeuristicSerial
from Heuristics.LiPaxsonHeuristic import LiPaxsonHeuristic
from typing import Dict, List
import csv
from tqdm import tqdm


config_path = './config.xml'

parser = argparse.ArgumentParser(description='Generate data files for vulnerability lifetime estimation.'
                                             'Default output write the csv to ./out/{configKey}.csv')
#parser.add_argument('key', help='Product key in the config xml')
parser.add_argument('commit', help='commit in the repository')

heuristics = ['vccfinder', 'vuldigger', 'vuldigger2', 'lipaxson']
parser.add_argument('-r', "--repo-path", dest='repo', required=True, type=str, help='Specify repository path')
parser.add_argument('-he', "--heuristic", required=True, type=str, choices=heuristics
                    , help='Specify the heuristic to use')

parser.add_argument('-c', "--config", type=str, help='Specify different config file')
parser.add_argument('-o', "--output", type=str, help='Specify different output file')
parser.add_argument('-j', "--java",  help='Set flag if the project is written in java', action='store_true')
parser.add_argument('-d', "--dsa",  help='Add boolean if the CVE is contained in the Debian security advisory. '
                                         'Requires a dla MongoDB to be running on the clinet', action='store_true')
parser.add_argument("-p", "--bar"
                    , help='Get a progressbar in the command line instead of a progress report every 100 mappings.'
                    , action='store_true')
parser.add_argument("-m", "--max-count", dest='maxcount', help="Limit the number of mappings", type=int)

parser.add_argument("-gt", "--ground-truth", dest='groundtruth'
                    , help="Specify a ground truth file. Check the readme for allowed configurations", type=str)

parser.add_argument("--delimiter", type=str, help="Specify a delimiter for the output csv file. Default is ';'")
parser.add_argument("--quote-char", dest='quotechar', type=str
                    , help="Specify a quotechar for the output csv file. Default is ' ")


args = parser.parse_args()
commit_sha = args.commit

if args.groundtruth:
    gt_path = args.groundtruth
else:
    gt_path = None

if args.output:
    out_path = args.output
else:
    if not os.path.exists('./out'):
        os.mkdir('./out')

if args.delimiter:
    delimiter = args.delimiter
else:
    delimiter = ';'

if args.quotechar:
    quotechar = args.quotechar
else:
    quotechar = '\''

if args.maxcount:
    maxcount = args.maxcount
else:
    maxcount = -1

repo_path = args.repo

if not os.path.exists(repo_path):
    raise OSError(f'Repository path "{repo_path}" not found!')

repo = Repo(repo_path)
if repo.bare:
    raise Exception('Found bare repository under \'{0}\'!'.format(repo_path))

print('Successfully loaded repository at \'{0}\''.format(repo_path))

print('Starting bic search...')

if args.heuristic == 'vuldigger2':
    heuristic = VuldiggerHeuristic2(repo, java=args.java)
    run_per_cve = False
elif args.heuristic == 'vuldigger':
    heuristic = VuldiggerHeuristic(repo, java=args.java)
    if args.java:
        warnings.warn('The chosen heuristic is not optimized for java and will therefore use c keywords and syntax!')
    run_per_cve = False
elif args.heuristic == 'vccfinder':
    heuristic = VccfinderHeuristicSerial(repo, java=args.java)
    run_per_cve = False
elif args.heuristic == 'lipaxson':
    heuristic = LiPaxsonHeuristic(repo, java=args.java)
    run_per_cve = False
else:
    raise NotImplementedError(f'The heuristic {args.heuristic} is currently not supported')

try:
    fixing_commit = repo.commit(commit_sha)
except ValueError:
    warnings.warn("Commit not found {0}".format(commit_sha))
except BadName:
    warnings.warn("Commit not found {0}".format(commit_sha))


res = heuristic.use_heuristic(fixing_commit, None)
print(f'heuristic execution finished.')
if res is None:
    print('No results')
else:
    print(sorted(res.items(), key=lambda x:x[1], reverse=True))
