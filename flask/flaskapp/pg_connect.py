import psycopg2
import psycopg2.extensions
import config
import json
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def connectPostgres(com_name, start_date, end_date):
    try:
        conn = psycopg2.connect(database=config.POSTGRES_CONFIG['dbname'],user=config.POSTGRES_CONFIG['user'],
                                password=config.POSTGRES_CONFIG['password'],host=config.POSTGRES_CONFIG['host'])
    except Exception as er:
        print("Unable to connect to the database")
        print(str(er))

    cur = conn.cursor ()
    cik = com_name
    start_date = start_date
    end_date = end_date
    cur.execute ( "select cik, country_iso_code, sum(count) as total from company_geo_table "
                  "where cik = %s and (date between %s and %s) "
                  "group by (cik, country_iso_code)",(cik, start_date, end_date))
    raw = cur.fetchall ()
    #data type: json
    # jsonData = json.dumps ( raw, cls=DecimalEncoder )
    cur.close ()
    conn.close ()
    return raw

