import logging
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from configs import config
from PIL import Image


SLACK_BOT_TEXT = (
    "Hey there! I found the result you want to ask."
    "I've listed them below. Following is a bar chart for"
    "easy visualization.\n\n*I hope you find it interesting!*\n"
)

class CovidFacade:

    def __init__(self, token=config.SLACK_BOT_TOKEN,
                 bot_name=config.SLACK_BOT_NAME):
        self.token = token
        self.default_channel = config.DEFAULT_SLACK_CHANNEL
        self.bot_name = bot_name

        # Internally set properites
        self.client = WebClient(token=self.token)
        self.BOT_ID = self.client.api_call("auth.test")['user_id']

        self.icon_emoji = ":mask:"
        self.slack_message_entries = {}

    def emit(self, message, file, channel):
        """Sends a message to your channel.
        Args:
            blocks: Expected to be a json-like array object containing the rich
                text representation of the listings we've found. The methods in
                this object should be used to construct the Rich Message Blocks.
                See the Slack kit builder for more information on block
                construction: https://app.slack.com/block-kit-builder
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

    def send_messages(self, messages, files, channel=None):
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

        