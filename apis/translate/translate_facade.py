import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from configs.config import *


class TranslateFacade:

    def __init__(self, token=SLACK_BOT_TOKEN,
                 bot_name=SLACK_BOT_NAME):
        self.token = token
        self.default_channel = DEFAULT_SLACK_CHANNEL
        self.bot_name = bot_name

        # Internally set properites
        self.client = WebClient(token=self.token)
        self.BOT_ID = self.client.api_call("auth.test")['user_id']

        self.icon_emoji = ":sab:"

    def emit(self, message, channel):
        """Sends a message to your channel.
        Args:
            message: string. Translated text.
            channel: string, The channel to send the message to.
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                username=self.bot_name,
                icon_emoji=self.icon_emoji
            )

        except SlackApiError as e:
            logging.error(f"Slack encountered an error: {e.response['error']}")
            raise e

        return response

    def send_messages(self, response, channel='#translate'):
        channel = channel or self.default_channel

        slack_response = self.emit(response, channel)

        logging.info(
            f"Response text from Slack {slack_response}")