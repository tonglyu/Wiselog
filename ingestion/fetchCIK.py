import urllib2
import csv
import psycopg2
import config

def write_to_csv(cik_data):
    fieldnames=["cik", "name"]
    with open ( 'cik_company.csv', 'w' ) as csv_file:
        writer = csv.DictWriter ( csv_file, fieldnames=fieldnames )
        writer.writeheader ()
        writer.writerows ( cik_data )

def read_data_url():
    url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
    cik_file = urllib2.urlopen(url)

    cik_data = []
    for line in cik_file:
        ele = line.split(':')
        tmp = {}
        tmp['cik'] = str(ele[1].strip()[3:])
        tmp['name'] = ele[0].strip()
        cik_data.append(tmp)

    return cik_data

if __name__ == '__main__':
    cik_data = read_data_url()
    conn = None
    sql_create_table = """
            CREATE TABLE cik_company (
                cik TEXT PRIMARY KEY NOT NULL,
                name VARCHAR(255) NOT NULL
            )
            """
    sql = """
    INSERT INTO cik_company(cik, name)
    VALUES(%s, %s)
    ON CONFLICT (cik) DO NOTHING;"""

    try:
        conn = psycopg2.connect ( database=config.POSTGRES_CONFIG['dbname'], user=config.POSTGRES_CONFIG['user'],
                          password=config.POSTGRES_CONFIG['password'], host=config.POSTGRES_CONFIG['host'] )
        cur = conn.cursor ()
        # print("create table")
        # cur.execute ( sql_create_table )
        for i in range(len(cik_data)):
            print(cik_data[i])
            cur.execute ( sql, (cik_data[i]['cik'], cik_data[i]['name']) )
            print("insert %d record", i)
        cur.close ()
        conn.commit()
    except Exception as er:
        print("cannot connect postgres")
        print(str ( er ))
    finally:
        if conn is not None:
            conn.close ()

    print("finish insert cik table")



