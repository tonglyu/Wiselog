from flask import Flask
from flask import render_template
import pg_connect

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    user = {'username': 'tong'}
    res = pg_connect.connectPostgres()
    data = []
    for i in range(len(res)):
        print(res[i])
        tmp = {}
        tmp['country'] = res[i][1]
        tmp['value'] = int(res[i][2])
        tmp['name'] = res[i][1]
        data.append(tmp)
    print(data)
    return render_template ( 'index.html', title='Home', user=user, data = data )

@app.route('/search')
def search():
    res = pg_connect.connectPostgres ()
    return render_template('map.html', data = res)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)
