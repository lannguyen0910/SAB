import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from configs.config import *


class LocationSearchFacade:

    def __init__(self, token=SLACK_BOT_TOKEN,
                 bot_name=SLACK_BOT_NAME):
        self.token = token
        self.default_channel = DEFAULT_SLACK_CHANNEL
        self.bot_name = bot_name

        # Internally set properites
        self.client = WebClient(token=self.token)
        self.BOT_ID = self.client.api_call("auth.test")['user_id']

        self.icon_emoji = ":robot_face:"

    def emit(self, message, channel):
        """Sends a message to your channel.
        Args:
            message: string. Blocks of location of places.
            channel: string, The channel to send the message to.
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                username=self.bot_name,
                icon_emoji=self.icon_emoji,
                **message
            )

        except SlackApiError as e:
            logging.error(f"Slack encountered an error: {e.response['error']}")
            raise e

        return response

    def send_messages(self, result, location, channel='#search'):
        channel = channel or self.default_channel
        message = self.display_search(result, location)
        slack_response = self.emit(message, channel)

        logging.info(
            f"Searched places from Slack {slack_response}")

    def display_search(self, response, location):
        if not response:
            return ":x: No businesses found."

        message = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "I found {} results in {}. :tada:\n".format(len(response), location or DEFAULT_LOCATION)
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
