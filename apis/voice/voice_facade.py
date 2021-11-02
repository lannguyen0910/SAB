import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from configs.config import *


class VoiceFacade:

    def __init__(self, token=SLACK_BOT_TOKEN,
                 bot_name=SLACK_BOT_NAME):
        self.token = token
        self.default_channel = DEFAULT_SLACK_CHANNEL
        self.bot_name = bot_name

        # Internally set properites
        self.client = WebClient(token=self.token)
        self.BOT_ID = self.client.api_call("auth.test")['user_id']

        self.icon_emoji = ":sab:"

    def emit(self, file, channel):
        try:
            file_response = self.client.files_upload(channels=channel, file=file) # upload image file to slack

        except SlackApiError as e:
            logging.error(f"Slack encountered an error: {e.response['error']}")
            raise e
        

        return file_response

    def send_messages(self, file, channel='#voice'):
        channel = channel or self.default_channel

        # Send voice file
        print('File: ', file)
        file_response = self.emit(file, channel)

        logging.info(
            f"Sent voice file {file} to Slack:\n{file_response}")
