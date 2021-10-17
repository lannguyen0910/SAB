import logging
import re

from configs.config import *
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient
from apis.text_generation.gpt2.src import generate_unconditional_samples


class GPT2Facade:

    def __init__(self, token=SLACK_BOT_TOKEN,
                 bot_name=SLACK_BOT_NAME):
        self.token = token
        self.default_channel = DEFAULT_SLACK_CHANNEL
        self.bot_name = bot_name

        # Internally set properites
        self.client = WebClient(token=self.token)
        self.BOT_ID = self.client.api_call("auth.test")['user_id']
        self.MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
        self.icon_emoji = ":wikipedia:"

    def emit(self, message, channel):
        """Sends a message to your channel.
        Args:
            message: string. Wiki searching texts.
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

    def send_messages(self, response, channel='#gpt2'):
        channel = channel or self.default_channel
        command = self.parse_bot_commands(response)
        message = generate_unconditional_samples.sample_model(nsamples=1,
                                                              length=min(
                                                                  3 * len(command), 300),
                                                              top_k=40,
                                                              command=command)
        slack_response = self.emit(message[0], channel)

        logging.info(
            f"Response text from Slack {slack_response}")

    def parse_bot_commands(self, response):
        """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
        """

        user_id, message = self.parse_direct_mention(response)
        if user_id == self.BOT_ID:
            return message
        return None

    def parse_direct_mention(self, message_text):
        """
            Finds a direct mention (a mention that is at the beginning) in message text
            and returns the user ID which was mentioned. If there is no direct mention, returns None
        """
        matches = re.search(self.MENTION_REGEX, message_text)
        # the first group contains the username, the second group contains the remaining message
        return (matches.group(1), matches.group(2).strip()) if matches else (
            None, None)
