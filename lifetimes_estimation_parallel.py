import argparse
import warnings
import xml.etree.ElementTree as ET
from Database.db_repository import DBRepository
from git import Repo, Commit, BadName
import os
from Heuristics.VuldiggerHeuristic2 import VuldiggerHeuristic2
from Heuristics.VuldiggerHeuristic import VuldiggerHeuristic
from Heuristics.VccfinderHeuristicSerial import VccfinderHeuristicSerial
from Heuristics.LiPaxsonHeuristic import LiPaxsonHeuristic
from typing import Dict, List
import csv
from pymongo import MongoClient
from tqdm import tqdm
from Utility.LifetimeEstimation import LifetimeEstimationHelper, ResultObject
import multiprocessing as mp
import pickle


config_path = './config.xml'

parser = argparse.ArgumentParser(description='Generate data files for vulnerability lifetime estimation.'
                                             'Default output write the csv to ./out/{configKey}.csv')
parser.add_argument('key', help='Product key in the config xml')

heuristics = ['vccfinder', 'vuldigger', 'vuldigger2', 'lipaxson']
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
parser.add_argument("-pc", "--process-count", dest='process_count', help="Max process count for multiprocessing", type=int)

parser.add_argument("-gt", "--ground-truth", dest='groundtruth'
                    , help="Specify a ground truth file. Check the readme for allowed configurations", type=str)

parser.add_argument("--delimiter", type=str, help="Specify a delimiter for the output csv file. Default is ';'")
parser.add_argument("--quote-char", dest='quotechar', type=str
                    , help="Specify a quotechar for the output csv file. Default is ' ")


args = parser.parse_args()

product_key = args.key
if args.config:
    config_path = args.config

if args.groundtruth:
    gt_path = args.groundtruth
else:
    gt_path = None

print('Loading config file...')

xml_root = ET.parse(config_path)

product_node = xml_root.find('.//product[@name=\'{0}\']'.format(product_key))

if product_node is None:
    raise ValueError('Product key \'{0}\' is not supported'.format(product_key))

out_path = f'./out/{product_key}_par.csv'

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

if args.process_count:
    process_count = min(os.cpu_count()+64,args.process_count)
else:
    process_count = 1

repo_path = product_node.find('./mapping/repo/path').text

if not os.path.exists(repo_path):
    raise OSError(f'Repository path "{repo_path}" not found!')

repo = Repo(repo_path)
if repo.bare:
    raise Exception('Found bare repository under \'{0}\'!'.format(repo_path))

print('Successfully loaded repository at \'{0}\''.format(repo_path))

db_repo = DBRepository()

print('Starting Lifetime estimation...')

if args.heuristic == 'vuldigger2':
    heuristic = VuldiggerHeuristic2(repo, java=args.java)
    run_per_cve = True
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

if gt_path is not None:
    if not os.path.exists(gt_path):
        raise OSError(f'Ground truth path "{gt_path}" not found!')
    gt_mappings = LifetimeEstimationHelper.gt_mappings(gt_path, repo)
    print(f'{len(gt_mappings)} ground truth mappings loaded!')
    mappings = LifetimeEstimationHelper.annotate_cve_information(gt_mappings)
    run_per_cve = True

else:
    mappings = db_repo.get_mappings(product_key, maxcount)
    print(f'{len(mappings)} Mappings loaded from DB for {product_key}')

commit_mappings = LifetimeEstimationHelper.group_mappings(mappings)


csvfile = open(out_path, 'w', newline='')
spamwriter = csv.writer(csvfile, delimiter=delimiter,
                        quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)
header = ['CVE'
    , 'Fixing sha'
    , 'Fixing date'
    , 'VCC-heuristic sha'
    , 'VCC-heuristic date'
    , 'VCC-oldest sha'
    , 'VCC-oldest date'
    , 'VCC-newest sha'
    , 'VCC-newest date'
    , 'Average date'
    , 'Weighted Average date'
    , 'CWE'
    , 'CVSS-Score'
    , 'CVSS-Vector'
    , 'Commits heuristic'
    , 'Commmits newest'
    , 'Commits oldest'
    , 'Commits weighted'
    , 'Stable']
if gt_path is not None:
    header.insert(3, 'VCC sha')
    header.insert(4, 'VCC date')
spamwriter.writerow(header)

if args.dsa:
    client = MongoClient()
    db = client.admin
    dla = db.dla
    dsa = db.dsa
else:
    dsa = None

count = 0

#if args.bar:
#    if run_per_cve:
#        pbar = tqdm(total=len(mappings), desc='Heuristic execution')
#    else:
#        pbar = tqdm(total=len(commit_mappings), desc='Heuristic execution')

#    for commit_sha, cves in commit_mappings.items():
def process_mapping(mapping):
    pid = os.getpid()
    (commit_sha, cves) = mapping
    try:
        fixing_commit = repo.commit(commit_sha)
    except ValueError:
        warnings.warn("Commit not found {0}".format(commit_sha))
        return -1
    except BadName:
        warnings.warn("Commit not found {0}".format(commit_sha))
        return -1

    if run_per_cve:
        row_ret = []
        for cve in cves:
            #print('Process ' + str(pid) + ' starting to process fixing commit: ' + commit_sha)
            res = LifetimeEstimationHelper.run_and_calculate(heuristic, fixing_commit, repo, cve)
            #print('Process ' + str(pid) + ' finished processing fixing commit: ' + commit_sha)
            if res is None:
            #    count += 1
            #    if args.bar:
            #        pbar.update(1)
            #    elif count % 100 == 0:
            #        print(f'Heuristic execution: {count}/{len(mappings)}')
                continue

            #print('Process ' + str(pid) + ' ready to write')
            res.stable = LifetimeEstimationHelper.check_dsa_vulnerable(cve, args.dsa, dsa)
            #lock.acquire()
            #spamwriter2 = csv.writer(csvfile, delimiter=delimiter,
            #            quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)
            #LifetimeEstimationHelper.writeline(spamwriter2, res, cve, gt=(gt_path is not None))
            #lock.release()
            #print('Process ' + str(pid) + ' sucessfully wrote to file')
            
            row = [cve['id']
            , res.fixing_commit.hexsha
            , res.fixing_commit.committed_datetime.strftime('%Y-%m-%d')
            , res.most_blamed.hexsha
            , res.most_blamed.committed_datetime.strftime('%Y-%m-%d')
            , res.oldest.hexsha
            , res.oldest.committed_datetime.strftime('%Y-%m-%d')
            , res.newest.hexsha
            , res.newest.committed_datetime.strftime('%Y-%m-%d')
            , res.average.strftime('%Y-%m-%d')
            , res.w_average.strftime('%Y-%m-%d')
            , cve['cwe-id']
            , cve['cvss-score']
            , cve['cvss_vector']
            , res.most_blamed_count
            , res.newest_count
            , res.oldest_count
            , res.w_average_count
            , res.stable
            ]
            
            gt=(gt_path is not None)
            if gt:
                if res.vcc is None:
                    row.insert(3, None)
                    row.insert(4, None)
                else:
                    row.insert(3, res.vcc.hexsha)
                    row.insert(4, res.vcc.committed_datetime.strftime('%Y-%m-%d'))
            row_ret.append(row)
            #count += 1
            #if args.bar:
            #    pbar.update(1)
            #elif count % 100 == 0:
            #    print(f'Heuristic execution: {count}/{len(mappings)}')
        return(row_ret)
    else:
        res = LifetimeEstimationHelper.run_and_calculate(heuristic, fixing_commit, repo, None)
        if res is None:
        #    count += 1
        #    if args.bar:
        #        pbar.update(1)
        #    elif count % 100 == 0:
        #        print(f'Heuristic execution: {count}/{len(mappings)}')
            return -1
        for cve in cves:
            res.stable = LifetimeEstimationHelper.check_dsa_vulnerable(cve, args.dsa, dsa)
            #spamwriter2 = csv.writer(csvfile, delimiter=delimiter,
            #            quotechar=quotechar, quoting=csv.QUOTE_MINIMAL)
            #lock.acquire()
            #LifetimeEstimationHelper.writeline(spamwriter2, res, cve, gt=(gt_path is not None))
            #lock.release()
            row = [cve['id']
            , res.fixing_commit.hexsha
            , res.fixing_commit.committed_datetime.strftime('%Y-%m-%d')
            , res.most_blamed.hexsha
            , res.most_blamed.committed_datetime.strftime('%Y-%m-%d')
            , res.oldest.hexsha
            , res.oldest.committed_datetime.strftime('%Y-%m-%d')
            , res.newest.hexsha
            , res.newest.committed_datetime.strftime('%Y-%m-%d')
            , res.average.strftime('%Y-%m-%d')
            , res.w_average.strftime('%Y-%m-%d')
            , cve['cwe-id']
            , cve['cvss-score']
            , cve['cvss_vector']
            , res.most_blamed_count
            , res.newest_count
            , res.oldest_count
            , res.w_average_count
            , res.stable
            ]
            
            gt=(gt_path is not None)
            if gt:
                if res.vcc is None:
                    row.insert(3, None)
                    row.insert(4, None)
                else:
                    row.insert(3, res.vcc.hexsha)
                    row.insert(4, res.vcc.committed_datetime.strftime('%Y-%m-%d'))
            return(row)
        #count += 1
        #if args.bar:
        #    pbar.update(1)
        #elif count % 100 == 0:
        #    print(f'Heuristic execution: {count}/{len(commit_mappings)}')
        return -1

def init(l):
    global lock
    lock = l

if __name__ == '__main__':
    print('Starting multi-process heuristic execution')
    l = mp.Lock()
    with mp.Pool(process_count,initializer=init, initargs=(l,)) as p:
        #result = list(tqdm(p.imap_unordered(process_mapping, commit_mappings.items(),chunksize=1), total=len(commit_mappings.items())))
        result = p.map(process_mapping, commit_mappings.items())
print(len(result))
cc = 0
for r in result:
    if r!= -1 and r is not None:
        for rr in r:
            cc += 1
            spamwriter.writerow(rr)

print(cc)
csvfile.close()
print(f'heuristic execution finished. Find your results under {out_path}')
