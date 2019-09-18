from flask import Flask, request
import re
import os
import sys
import time
import slack
from slackeventsapi import SlackEventAdapter
import threading

app = Flask(__name__)

# select the bot's oauth access token to post as the bot
slack_token = os.environ["BOT_SLACK_OAUTH_ACCESS"]
client = slack.WebClient(token=slack_token)

# signing secret
slack_secret =  os.environ["SLACK_SECRET"]

# event handler for the events api
# initialize with a secret - this is also to verify that requests come from slack
slack_events = SlackEventAdapter(slack_secret, "/slack/events")

# set port
PORT = 4390


@app.route('/')
def homepage():
    return "Howdy hacker!"

@app.route('/verify', methods=['POST'])
def verification():
    print(request.headers)
    print(request.get_json())
    # sys.stdout.flush()
    return "HTTP 200 OK Content-type: text/plain " + request.get_json['challenge']


@app.route('/github-manager-test', methods=['POST'])
def scheduleme():
    return os.environ["DARK_SKY_API"]

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
    
    return "Added users " + ', '.join(raw_text) + 'to the Isomer organization'
    
@app.route('/remove-user', methods=['POST'])
def removeUser():    
    # get the full request from Slack
    slack_request = request.form

    # starting a new thread for doing the actual processing    
    x = threading.Thread(
            target=removeUserAction,
            args=(slack_request,)
        )

    x.start()
    
    return {"Your mom"}

    
def removeUserAction(slack_request):
    # test using the slack client's methods
    channel_id =  slack_request['channel_id']

    client.chat_postMessage(
        channel=channel_id,
        text="Hello from your app! :tada:")


if __name__ == '__main__':
    app.run(debug=True, port=PORT)
