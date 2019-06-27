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
        com_name = request.form['com_name']
        res = pg_connect.connectPostgres (com_name)
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
