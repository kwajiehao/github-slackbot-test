from flask import Flask, request
import re

app = Flask(__name__)

PORT = 4390


@app.route('/')
def homepage():
    return "Howdy hacker!"


@app.route('/github-manager-test', methods=['POST'])
def scheduleme():
    return "It's time to run some tests"

@app.route('/add-user', methods=['POST'])
def addUser():
    # get the text sent together with the slash command
    raw_text = request.form.get('text').split(' ')

    # error handling
    # this can be something as simple as ensuring this is a valid email address
    # here, we allow only a max of two users
    if len(raw_text) > 2:
        return 'Maximum number of users that can be added at one time is 2'
    
    for user in raw_text:
        print(user)
    
    return "Added users " + ', '.join(raw_text)
    
    
        
    



if __name__ == '__main__':
    app.run(debug=True, port=PORT)
