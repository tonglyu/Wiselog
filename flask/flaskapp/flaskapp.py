from flask import Flask, render_template, request
import pg_connect

app = Flask(__name__)
user = {'username': 'tong'}

@app.route('/')
@app.route('/home')
def index():
    return render_template ( 'index.html')

@app.route('/search',methods=['Get', 'POST'])
def search_name():
    if request.method == "POST":
        keyword = request.form['keyword']
        method = request.form['search_method']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        res = pg_connect.connectPostgres (keyword, method, start_date, end_date)
    data = []
    for i in range ( len ( res ) ):
        tmp = {}
        tmp['country'] = res[i][1]
        tmp['value'] = int ( res[i][2] )
        tmp['name'] = res[i][1]
        data.append ( tmp )
    return render_template('map.html', data = data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)
