from flask import Flask
from flask import render_template
   
app = Flask(__name__)

@app.route('/')
def index():
    user = {'username': 'tong'}
    return render_template ( 'index.html', title='Homepage', user=user )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
