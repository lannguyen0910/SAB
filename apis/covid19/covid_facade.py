import logging
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from configs.config import *
from PIL import Image


class CovidFacade:

    def __init__(self, token=SLACK_BOT_TOKEN,
                 bot_name=SLACK_BOT_NAME):
        self.token = token
        self.default_channel = DEFAULT_SLACK_CHANNEL
        self.bot_name = bot_name

        # Internally set properites
        self.client = WebClient(token=self.token)
        self.BOT_ID = self.client.api_call("auth.test")['user_id']

        self.icon_emoji = ":mask:"

    def emit(self, message, file, channel):
        """Sends a message to your channel.
        Args:
            message: string. Covid info in the country from Covid API.
            file: string. Path to image which plots the Covid API info such as: [Confirmed Cases | Deaths | Recovered Cases].
            channel: string, The channel to send the message to.
        """
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                username=self.bot_name,
                icon_emoji=self.icon_emoji
            )
            self.post_image_to_slack(file, channel)

        except SlackApiError as e:
            logging.error(f"Slack encountered an error: {e.response['error']}")
            raise e

        return response

    def send_messages(self, messages, files, channel='#covid'):
        channel = channel or self.default_channel

        # Send messages
        for ind, (file, message) in enumerate(zip(files,messages)):
            print('File: ', file)
            slack_response = self.emit(message, file, channel)
            logging.info(
                f"Sent message {ind+1}/{len(messages)} to Slack:\n{slack_response}")
        
        logging.info(
            f"Sent all {len(messages)} messages to Slack.")

    def post_image_to_slack(self, file, channel):
        url = "https://slack.com/api/files.upload"

        # with open(file, 'r') as fh:
        #     image_data = fh.read()
        image_data = Image.open(file)
        image_data.show()

        data = {
            "token": self.token,
            "channels": channel,
            "content": image_data,
            "filename": "files",
            "filetype": "png",
        }

        response = requests.post(
            url=url, data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"})

        if response.status_code == 200:
            print("successfully completed post image to slack "
                        "and status code %s" % response.status_code)
        else:
            print("Failed to post image on slack channel "
                        "and status code %s" % response.status_code)

        