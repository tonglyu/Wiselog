from flask_sqlalchemy import SQLAlchemy
import config
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

def getCompanies(engine, name):
    conn = engine.connect ()
    name = '%'+name.upper()+'%'
    companies_sql = ''' select cik, name from cik_company where name like %s;'''
    companies = conn.execute(companies_sql,name)
    conn.close()
    return companies.fetchall()

def seachAcessCount(conn,keyword, method, start_date, end_date):
    start_date = start_date
    end_date = end_date

    print(method)
    begin = time.time ()
    cik = keyword
    name = conn.execute('''select name from cik_company where cik = %s''', cik).fetchall()

    country_query = '''
    select country_iso_code, sum(count) as total 
    from log_geolocation
    where cik = %s and (date between %s and %s) 
    group by country_iso_code
    '''
    country = conn.execute ( country_query, (cik, start_date, end_date) )
    city_query = '''
    select log.total as total, coord.country_name as country_name, coord.region_name as region, 
    coord.city_name as city, coord.lat as lat, coord.lng as lng
    from city_coordinates coord,
    (select geoname_id, sum(count) as total from log_geolocation
                             where cik = %s and (date between %s and %s)
                             group by geoname_id order by total desc limit 20) log
    where log.geoname_id = coord.geoname_id'''
    city = conn.execute ( city_query, (cik, start_date, end_date) )

    end = time.time ()
    print(end - begin)
    return str(name[0][0]).title(), country.fetchall(), city.fetchall()
