import pandas as pd
import csv


def clean_up(data_path, gt_path):
    df = pd.read_csv(data_path, sep=';')
    print(f'Loaded {df.shape[0]} entries')
    df_gt = pd.read_csv(gt_path, sep='  ')

    dels = []

    for row, data in enumerate(df.values):
        df_gt_row = df_gt.loc[(df_gt['Fixing Commit'] == data[1]) & (df_gt['CVE'] == data[0])]
        if df_gt_row.shape[0] == 0:
            dels.append(row)

    df.drop(dels, inplace=True)

    print(f'Removed {len(dels)} entries. {df.shape[0]} remaining.')
    df.to_csv(data_path, sep=';', quotechar='\'', quoting=csv.QUOTE_MINIMAL, index=False)


if __name__ == '__main__':
    clean_up('../../Data/Lifetimes/GroundTruth/chrome_gt.csv', '../../Data/GroundTruthMappings/chromium_gt.txt')
    clean_up('../../Data/Lifetimes/GroundTruth/chrome_gt_lipaxson.csv', '../../Data/GroundTruthMappings/chromium_gt.txt')
    clean_up('../../Data/Lifetimes/GroundTruth/httpd_gt.csv', '../../Data/GroundTruthMappings/httpd_gt.txt')
    clean_up('../../Data/Lifetimes/GroundTruth/httpd_lipaxson_gt.csv', '../../Data/GroundTruthMappings/httpd_gt.txt')