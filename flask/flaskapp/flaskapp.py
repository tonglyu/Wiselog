from flask import Flask
from flask import render_template
import pg_connect

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'tong'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    res = pg_connect.connectPostgres()
    print(res)
    return render_template ( 'index.html', title='Home', user=user, posts=posts, result = res )

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)
