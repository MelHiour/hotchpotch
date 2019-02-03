from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def base_form():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def graphing():
    date_from = request.form['date_from']
    date_until = request.form['date_until']
    return (date_from+date_until) 

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True)
