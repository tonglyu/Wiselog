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


def connectPostgres():
    try:
        conn = psycopg2.connect(database=config.POSTGRES_CONFIG['dbname'],user=config.POSTGRES_CONFIG['user'],
                                password=config.POSTGRES_CONFIG['password'],host=config.POSTGRES_CONFIG['host'])
    except Exception as er:
        print("Unable to connect to the database")
        print(str(er))

    cur = conn.cursor ()
    cik = '1288776'
    start_date = '2016-03-01'
    end_date = '2016-03-31'
    cur.execute ( "select cik, city_name, sum(count) as total from company_geo_table "
                  "where cik = %s and (date between %s and %s) "
                  "group by (cik, city_name)"
                  "order by total desc limit 20;",(cik, start_date, end_date))
    raw = cur.fetchall ()
    #data type: json
    jsonData = json.dumps ( raw, cls=DecimalEncoder )
    cur.close ()
    conn.close ()
    return jsonData

