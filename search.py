import os
import requests
import string
from slack_sdk import WebClient
from pathlib import Path
from flask import Flask, Response, request
from slackeventsapi import SlackEventAdapter
from yelp.client import Client
from dotenv import load_dotenv


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# Create an events adapter and register it to an endpoint in the slack app for event injestion.
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

slack_web_client = WebClient(token=os.environ['SLACK_TOKEN'])

BOT_ID = slack_web_client.api_call("auth.test")['user_id']
yelp_web_client = Client(os.environ['YELP_API_KEY'])

# ---------------------------------------------------------------------------
headers = {'Authorization': 'Bearer {}'.format(os.environ['YELP_API_KEY'])}
search_api_url = 'https://api.yelp.com/v3/businesses/search'
default_limit = os.environ['DEFAULT_LIMIT']  # Ex: 5
default_location = os.environ['DEFAULT_LOCATION']  # Ex: Berlin, Singapore,...
api_key = os.environ['YELP_API_KEY']
headers = {
    'Authorization': 'Bearer %s' % api_key,
}
# ---------------------------------------------------------------------------

welcome_messages = {}
message_counts = {}  # reset when re-run the server, needs database for fixed storing
BAD_WORDS = ['sheesh', 'hate', ]  # you can add some bad words you like xD


class WelcomeMessage:
    START_TEXT = {
        'type': 'section',
        'text': {
            'type': 'mrkdwn',
            'text': (
                'Welcome to this awesome channel! :heart:\n'
                'Get started by completing the step below.'
            )
        }
    }

    DIVIDER = {'type': 'divider'}

    def __init__(self, channel, user):
        self.channel = channel
        self.user = user
        self.icon_emoji = ':robot_face:'
        self.timestamp = ''
        self.completed = False

    def get_message(self):
        return {
            'ts': self.timestamp,
            'channel': self.channel,
            'icon_emoji': self.icon_emoji,
            'username': 'Welcome Bot!',
            'blocks': [
                self.START_TEXT,
                self.DIVIDER,
                *self._get_reaction_task()
            ]
        }

    def _get_reaction_task(self):
        checkmark = ':white_check_mark:'
        if not self.completed:
            checkmark = ':white_large_square:'

        text = f'{checkmark} *Add an emoji reaction to show how you feel today. 🤔*'

        return [{'type': 'section', 'text': {'type': 'mrkdwn', 'text': text}}]


def send_welcome_message(channel, user):
    if channel not in welcome_messages:
        welcome_messages[channel] = {}

    if user in welcome_messages[channel]:
        return

    welcome = WelcomeMessage(channel, user)
    message = welcome.get_message()
    response = slack_web_client.chat_postMessage(**message)
    welcome.timestamp = response['ts']

    welcome_messages[channel][user] = welcome


def check_if_bad_words(message):
    msg = message.lower()
    # construct translation table
    msg.translate(str.maketrans('', '', string.punctuation))

    return any(word in msg for word in BAD_WORDS)   # List of TRUE/FALSE in msg


def search(term, location):
    params = {
        'term': term,
        'location': location or default_location,
        'open_now': True,
        'limit': default_limit
    }
    response = requests.get(search_api_url, headers=headers, params=params)
    print('Response: ', response.json())
    return response.json()['businesses']


def display_search(response, location):
    if not response:
        return ":x: No businesses found."

    message = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "I found {} results in {}. :tada:\n".format(len(response), location or default_location)
                }
            },
        ]}

    for venue in response:
        categories = []
        if not venue['is_closed']:
            [categories.append(a['title']) for a in venue['categories']]
            divider = {
                "type": "divider"
            }

            trans = ":heavy_check_mark:" + " Takeout"
            if "delivery" in venue['transactions']:
                trans += " :heavy_check_mark: " + "Delivery"

            section = {
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                        "text": "*{name}* - {rating} :star: {review_count} reviews\n_{categories}_\nPhone: {phone}\n{trans}\n".format(
                                name=venue['name'],
                                rating=venue['rating'],
                                review_count=venue['review_count'],
                                categories=", ".join(categories),
                                phone=venue['display_phone'],
                                trans=trans)
                },
                "accessory": {
                    "type": "image",
                    "image_url": venue['image_url'],
                    "alt_text": "alt text for image"
                }
            }

            location = {
                "type": "context",
                "elements": [
                        {
                            "type": "plain_text",
                            "emoji": True,
                            "text": ":round_pushpin:" + ", ".join(venue['location']['display_address'])
                        }
                ]
            }

            button = {
                "type": "actions",
                "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Go to Yelp",
                                "emoji": True
                            },
                            "value": "click_me_123",
                            "url": venue['url']
                        },
                ]
            }

            for item in [divider, section, location, button]:
                message["blocks"].append(item)

    return message


def show_commands(user):
    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Hello <@%s> :wave: ! I'm so glad that you are here.\nBot-Search allows you perform Yelp search from right within Slack." % user
                }
            }],
        "attachments": [
            {
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":paw_prints: *Commands* :paw_prints:"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                "`search [bussiness]` Returns top 10 bussinesses in Berlin, Germany.\n\n"
                                "`search [bussiness], [location]` Returns 10 bussinesses based on the provided location."
                            )
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": ":paw_prints: *Examples* :paw_prints:"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": (
                                "`search ramen`\n\n"
                                "`search milk tea`\n\n"
                                "`search popcorn chicken, Berlin`"
                            )
                        }
                    }
                ]
            }
        ]
    }


@slack_event_adapter.on('message')
# Handle all message events
def handle_message(payload):
    # payload is all the information from the API
    event = payload.get('event', {})
    user_id = event.get('user')
    channel_id = event.get('channel')
    text = event.get('text')

    default_message = "I'm sorry. I don't understand."
    message = None

    if check_if_bad_words(text):
        ts = event.get('ts')
        # Reply in thread
        slack_web_client.chat_postMessage(
            channel=channel_id, thread_ts=ts, text='You should not have said that!!!')

        return Response(), 200

    if user_id != None and BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1

        if text.lower() == 'hello' or text.lower() == 'hi':
            send_welcome_message(channel_id, user_id)

        elif "search" in text.lower():
            user_response = text[6:].split(", ")
            location = None
            if len(user_response) > 1:
                location = user_response[1]
            term = user_response[0]
            result = search(term, location)
            message = display_search(result, location)
            slack_web_client.chat_postMessage(channel=channel_id, **message)
            return Response(), 200

        else:
            slack_web_client.chat_postMessage(
                channel=channel_id, text=default_message)


@slack_event_adapter.on('reaction_added')
def reaction(payload):
    event = payload.get('event', {})
    user_id = event.get('user')
    # this event is a bit different than above
    channel_id = event.get('item', {}).get('channel')

    if channel_id not in welcome_messages:
        return

    welcome = welcome_messages[channel_id][user_id]
    welcome.completed = True    # task is completed
    message = welcome.get_message()
    updated_message = slack_web_client.chat_update(
        **message)   # update emoji by adding reaction
    welcome.timestamp = updated_message['ts']

    if welcome.completed:
        response = show_commands(user_id)
        slack_web_client.chat_postMessage(channel=channel_id, **response)


@app.route('/messages-count', methods=['POST'])
def messages_count():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_count = message_counts.get(user_id, 0)

    slack_web_client.chat_postMessage(
        channel=channel_id, text=f'Message counts: {message_count}')

    return Response(), 200


if __name__ == "__main__":
    # flask app run on default port 5000 and automatically update server
    app.run(debug=True)
