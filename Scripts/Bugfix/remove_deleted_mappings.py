import mysql.connector
import pandas as pd
import csv

config = {
    'user': 'mbrack',
    'password': 'GK4zNrqK',
    'host': '130.83.163.37',
    'database': 'cve_mappings',
}

def remove_manual_deltes(product_key, data_path):

    print(product_key)
    print(data_path)

    cnx = mysql.connector.connect(auth_plugin='mysql_native_password', **config)
    cursor = cnx.cursor()


    sql = """SELECT DISTINCT cve.cve_id, commit.com_sha, link_cve_fixing_commit.manual_delete
    FROM cve
    INNER JOIN cve_config_code ON cve_config_code.cve_id = cve.cve_id
    INNER JOIN link_cve_fixing_commit ON link_cve_fixing_commit.cve_id =  cve.cve_id and link_cve_fixing_commit.com_config_code = cve_config_code.config_code
    INNER JOIN commit ON commit.com_sha = link_cve_fixing_commit.com_sha AND commit.com_config_code = link_cve_fixing_commit.com_config_code
    WHERE cve_config_code.config_code =  %s"""

    cursor.execute(sql, [product_key])

    mappings = cursor.fetchall()
    cursor.close()

    df_db = pd.DataFrame(mappings, columns=['cve', 'fix', 'man_del'])

    df = pd.read_csv(data_path, sep=';')
    print(f'Loaded {df.shape[0]} entries')

    dels = []

    for row, data in enumerate(df.values):
        df_gt_row = df_db.loc[(df_db.fix == data[1]) & (df_db.cve == data[0])]
        if df_gt_row.shape[0] == 0:
            print(f'Iconsistent data: Mapping {data[0]} | {data[1]} not in db')
            return
        if df_gt_row.man_del.max() == 1:
            dels.append(row)

    df.drop(dels, inplace=True)

    print(f'Removed {len(dels)} entries. {df.shape[0]} remaining.')
    df.to_csv(data_path, sep=';', quotechar='\'', quoting=csv.QUOTE_MINIMAL, index=False)
    print()
    print('=' *100)
    print()

if __name__ == '__main__':
    remove_manual_deltes('firefox', '../../Data/Lifetimes/firefox.csv')
    remove_manual_deltes('firefox', '../../Data/Lifetimes/firefox_lipaxson.csv')
    remove_manual_deltes('chrome', '../../Data/Lifetimes/chrome.csv')
    remove_manual_deltes('chrome', '../../Data/Lifetimes/chrome_lipaxson.csv')
    remove_manual_deltes('httpd', '../../Data/Lifetimes/httpd.csv')
    remove_manual_deltes('httpd', '../../Data/Lifetimes/httpd_lipaxson.csv')
    remove_manual_deltes('kernel', '../../Data/Lifetimes/kernel.csv')
    #remove_manual_deltes('', '../../Data/Lifetimes/')
    remove_manual_deltes('openssl', '../../Data/Lifetimes/openssl.csv')
    remove_manual_deltes('openssl', '../../Data/Lifetimes/openssl_lipaxson.csv')
    remove_manual_deltes('php', '../../Data/Lifetimes/php.csv')
    remove_manual_deltes('postgres', '../../Data/Lifetimes/postgres.csv')
    remove_manual_deltes('postgres', '../../Data/Lifetimes/postgres_lipaxson.csv')
    remove_manual_deltes('qemu', '../../Data/Lifetimes/qemu.csv')
    remove_manual_deltes('qemu', '../../Data/Lifetimes/qemu_lipaxson.csv')
    remove_manual_deltes('tcpdump', '../../Data/Lifetimes/tcpdump.csv')
    remove_manual_deltes('tcpdump', '../../Data/Lifetimes/tcpdump_lipaxson.csv')
    remove_manual_deltes('wireshark', '../../Data/Lifetimes/wireshark.csv')
    remove_manual_deltes('wireshark', '../../Data/Lifetimes/wireshark_lipaxson.csv')
