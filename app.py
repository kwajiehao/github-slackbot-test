from flask import Flask

app = Flask(__name__)

PORT = 4390


@app.route('/')
def homepage():
    return "Howdy hacker!"


@app.route('/github-manager-test', methods=['POST'])
def scheduleme():
    return "It's time to run some tests"



if __name__ == '__main__':
    app.run(debug=True, port=PORT)
