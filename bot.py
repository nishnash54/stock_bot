import random
import requests
import json
from env import var
from flask import Flask, request
from pymessenger.bot import Bot

app = Flask(__name__)
ACCESS_TOKEN = var.access_token
VERIFY_TOKEN = var.verify_token
api_key = var.apikey
link = "https://www.alphavantage.co/query"
bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       # print(output)
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:
            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                recipient_id = message['sender']['id']
                if message['message'].get('text'):
                    response_sent_text = get_message(message['message']['text'])
                    send_message(recipient_id, response_sent_text)
                #if user sends us a GIF, photo,video, or any other non-text item
                if message['message'].get('attachments'):
                    response_sent_nontext = "Sorry.\nI did not get you.\nTry help for a list of commands."
                    send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


#chooses a random message to send to the user
def get_message(msg):
    if msg == 'help':
        resp = "Enter trade symbol of any company."
    else:
        try:
            parameters = {'function': 'TIME_SERIES_INTRADAY', 'interval': '1min', 'symbol': msg, 'apikey': api_key}
            r = requests.get(url = link, params = parameters)
            data = json.loads(r.text)
            val = {}
            for each in data['Time Series (1min)']:
                val[each] = data['Time Series (1min)'][each]['1. open']
                break
            resp = msg + " : $" + str(val[list(val.keys())[0]])
        except:
            resp = "Sorry.\nI did not get you.\nTry help for a list of commands."
    # return selected item to the user
    return resp

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    app.run()
