from flask_sqlalchemy import SQLAlchemy
import config
import os
import time

def init_db(app):
    global db
    # the values of those depend on your setup
    user = config.POSTGRES_CONFIG['user']
    password = config.POSTGRES_CONFIG['password']
    database = config.POSTGRES_CONFIG['dbname']
    host = config.POSTGRES_CONFIG['host']
    port = config.POSTGRES_CONFIG['port']

    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}'.format(user=user,pw=password,host=host, port=port,db=database)

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

    db = SQLAlchemy(app)

    # db.create_all()


def seachAcessCount(conn,keyword, method, start_date, end_date):

    start_date = start_date
    end_date = end_date

    print(method)
    begin = time.time ()
    if method == "cik":
        cik = keyword
        country = conn.execute ( "select cik, country_iso_code, sum(count) as total from company_geo_table "
                      "where cik = %s and (date between %s and %s) "
                      "group by (cik, country_iso_code)", (cik, start_date, end_date) )
        city_query = '''
        select log.cik as cik, log.total as total, coord.country_iso_code as country_code, coord.region_name as region, 
        coord.city_name as city, coord.lat as lat, coord.lng as lng
        from (select cik, geoname_id, sum(count) as total from company_geo_table
                                 where cik = %s and (date between %s and %s)
                                 group by (cik, geoname_id) order by total desc limit 20) log
        left join city_coordinates coord on log.geoname_id = coord.geoname_id limit 20
                                 '''
        city = conn.execute ( city_query, (cik, start_date, end_date) )

    else:
        name = keyword.upper ()
        print(name)
        country = conn.execute ( "select cik, country_iso_code, sum(count) as total from company_geo_table "
                      "where cik = (select cik from cik_company where name = %s) and (date between %s and %s) "
                      "group by (cik, country_iso_code)", (name, start_date, end_date) )
        city_query = '''
                select log.cik as cik, log.total as total, coord.country_iso_code as country_code, coord.region_name as region, 
                coord.city_name as city, coord.lat as lat, coord.lng as lng
                from (select cik, geoname_id, sum(count) as total from company_geo_table
                                 where cik = (select cik from cik_company where name = %s) and (date between %s and %s)
                                 group by (cik, geoname_id) order by total desc limit 20) log
                left join city_coordinates coord on log.geoname_id = coord.geoname_id limit 20
                                         '''
        city = conn.execute (city_query, (name, start_date, end_date) )

    end = time.time ()
    print(end - begin)
    return country.fetchall(), city.fetchall()
