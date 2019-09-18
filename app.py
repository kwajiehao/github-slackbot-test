from flask import Flask, request
import re
import os
import sys
import time
import slack
import requests
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
    
    # Used for verification
    #print(request.headers)
    #print(request.get_json())
    #payload = request.get_json()
    ## return "HTTP 200 OK Content-type: application/json " + '{"challenge":"' + payload['challenge'] + '"}'
    #return "HTTP 200 OK Content-type: text/plain " + payload['challenge']

    # get the full request from Slack
    slack_request = request.get_json()
    channel_id =  slack_request['event']['channel']

    # starting a new thread for doing the actual processing 
    # because slack requires a response within 3000ms   
    x = threading.Thread(
            target=test,
            args=(slack_request,)
        )
    x.start()

    y = threading.Thread(
            target=responseToUser,
            args=(slack_request,)
        )
    y.start()

    print(slack_request)

    return "We are processing your request..."

    
def test(slack_request):
    # test using the slack client's methods
    channel_id =  slack_request['event']['channel']

    # ensure the bot doesn't respond to itself
    try:
        print(slack_request['event']['bot_id'])
    except KeyError:
        client.chat_postMessage(
            channel=channel_id,
            text="Hello from your app! :tada:")


def responseToUser(slack_request):
    try:
        callback_id = slack_request['callback_id']
        if callback_id == 'github-manager-test':
            if slack_request['actions']['value'] == 'yes':
                client.chat_postMessage(
                    channel=channel_id,
                    text="We have added the user to your organization"
                )
            elif slack_request['actions']['value'] == 'no':
                client.chat_postMessage(
                    channel=channel_id,
                    text="We have not added the user to your organization"
                )

    except:
        print("there is an error")


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
    print(request.form)

    # starting a new thread for doing the actual processing 
    # because slack requires a response within 3000ms   
    x = threading.Thread(
            target=removeUserAction,
            args=(slack_request, )
        )

    x.start()

    return "Processing your request..."

    
def removeUserAction(slack_request):
    # test using the slack client's methods
    channel_id =  slack_request['channel_id']

    client.chat_postMessage(
        channel=channel_id,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Chew choo! @scott started a train to Deli Board at 11:30. Will you join?"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Yes",
                            "emoji": True
                        },
                        "action_id": 'add-or-remove:yes',
                        "value": 'yes'
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "No",
                            "emoji": True
                        },
                        "action_id": 'add-or-remove:no',
                        "value": 'no'
                    }
                ]
            }
        ])


@app.route('/interaction', methods=['POST'])
def interactionTest():
    # check the request components
    slack_request = request.form
    print(request.headers)
    # print(slack_request)

    #x = threading.Thread(
    #        target=removeUserAction,
    #        args=(slack_request, )
    #    )
    #x.start()
    return 'test'

def removeUserAction(slack_request):
    try:
        payload = slack_request.get('payload')
        responseUrl = payload['response_url']
        actionValue = payload['actions']['value']
        action = payload['actions']['action_id'].split(':')[0]

        if action == 'add-or-remove':
            if actionValue == 'yes':
                # remove user
                payload = {
                    "text": "The user has been removed"
                }
            elif actionValue == 'no':
                # do not remove user
                payload = {
                    "text": "The user has NOT been removed"
                }
            r = requests.post(responseUrl, json=payload)
            print('response from server:',r.text)
        except:
            print('there is an error')

if __name__ == '__main__':
    app.run(debug=True, port=PORT)
