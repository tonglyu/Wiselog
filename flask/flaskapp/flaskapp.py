from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, func
from sqlalchemy import Column, BigInteger, String, Date
from sqlalchemy.orm import sessionmaker

import json
import postgresDB

app = Flask(__name__)
app.config['DEBUG'] = True
user = {'username': 'tong'}

postgresDB.init_db(app)
db = postgresDB.db

engine = db.get_engine()
metadata = MetaData()
company_geo_table = Table('company_geo_table', metadata,
                          Column ( 'geoname_id', String ),
                          Column ('date', Date),
                          Column ('cik', String),
                          Column ('count', BigInteger),
                          Column ('country_iso_code', String),
                          Column ('subdivision_1_name', String),
                          Column ('city_name', String),
                          autoload=True, autoload_with=engine)

Session = sessionmaker(bind=engine)
session = Session()


@app.route('/')
@app.route('/home')
def index():
    return render_template ( 'index.html',list=[])

@app.route('/searchCom', methods=["POST"])
def search_company():
    keyword = request.form['keyword']
    companies_res = postgresDB.getCompanies ( engine, keyword )
    companies = []
    for i in range ( len ( companies_res) ):
        tmp = {}
        tmp["cik"] = companies_res[i][0]
        tmp["name"] = str ( companies_res[i][1]  ).strip ().title ()
        companies.append ( tmp )
    return json.dumps(companies)

@app.route('/search',methods=['GET', 'POST'])
def search_name():
    if request.method == "POST":
        method = request.form['search_method']
        if method == "cik":
            cik = request.form['keyword']
        else:
            cik = request.form['company_selector']

        start_date = request.form['start_date']
        end_date = request.form['end_date']

        conn = engine.connect()
        name, country_res, city_res = postgresDB.seachAcessCount(conn, cik, method, start_date, end_date)
        conn.close()
    period = 'From ' + start_date + ' to ' + end_date
    country_data = []
    for i in range ( len ( country_res ) ):
        tmp = {}
        tmp['country'] = country_res[i][0]
        tmp['value'] = int ( country_res[i][1] )
        tmp['name'] = country_res[i][0]
        country_data.append ( tmp )

    city_data = []
    for i in range ( len ( city_res ) ):
        tmp = {}
        tmp['value'] = int ( city_res[i][0])
        tmp['country'] = city_res[i][1]
        tmp['region'] = city_res[i][2]
        tmp['name'] = city_res[i][3]
        tmp['lat'] = city_res[i][4]
        tmp['lon'] = city_res[i][5]
        city_data.append ( tmp )

    return render_template('map.html', title="Query result", cik=cik, name=name, period=period,country_data = country_data, city_data = city_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)
