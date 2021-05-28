from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    if request.method == 'GET':
        return render_template('hello.html')


@app.route('/add_data', methods=['GET', 'POST'])
def enter_expense():
    if request.method == 'GET':
        return render_template('enter_data.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
