import logging
import urllib
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from .overflow_helper import OverflowHelper
from configs.config import *


class OverflowFacade:

    def __init__(self, token=SLACK_BOT_TOKEN,
                 bot_name=SLACK_BOT_NAME):
        self.token = token
        self.default_channel = DEFAULT_SLACK_CHANNEL
        self.bot_name = bot_name

        # Internally set properites
        self.client = WebClient(token=self.token)
        self.BOT_ID = self.client.api_call("auth.test")['user_id']
        self.helper = OverflowHelper()
        self.icon_emoji = ":wikipedia:"

    def emit(self, response, channel):
        """Sends a message to your channel.
        Args:
            message: string. Wiki searching texts.
            channel: string, The channel to send the message to.
        """
        try:
            title, link, text = response
            response = self.client.chat_postMessage(
                channel=channel,
                attachments=[
                    {
                        "title": title,
                        "pretext": link,
                        "text": text,
                        "mrkdwn_in": ["text"]
                    }
                ],
                username=self.bot_name,
                icon_emoji=self.icon_emoji
            )

        except SlackApiError as e:
            logging.error(f"Slack encountered an error: {e.response['error']}")
            raise e

        return response

    def send_messages(self, query, channel='#stackoverflow'):
        channel = channel or self.default_channel

        response = self.generate_answer(query, False)

        slack_response = self.emit(response, channel)

        logging.info(
            f"Response text from Slack {slack_response}")

    # def reply_thread(self, thread_ts, channel, response):
    #     title, link, text = response
    #     self.client.chat_postMessage(
    #         channel=channel,
    #         attachments=[
    #             {
    #                 "title": title,
    #                 "pretext": link,
    #                 "text": text,
    #                 "mrkdwn_in": ["text"]
    #             }
    #         ],
    #         thread_ts=thread_ts
    #     )

    # def post_to_channel(self, channel, response):
    #     title, link, text = response
    #     self.client.api_call(
    #         "chat.postMessage",
    #         channel=channel,
    #         attachments=[
    #             {
    #                 "title": title,
    #                 "pretext": link,
    #                 "text": text,
    #                 "mrkdwn_in": ["text"]
    #             }
    #         ]
    #     )

    # def parse_events(self, slack_events):
    #     for event in slack_events:
    #         # TODO: Make sure that we at least take care of the obvious edge cases.
    #         if event["type"] == "message":
    #             if "subtype" in event:
    #                 # Ignore bot messages
    #                 if event["subtype"] == "bot_message":
    #                     return

    #             if "text" in event:
    #                 message = event["text"]
    #                 # If DMing bot
    #                 if event["channel"][0] == "D":
    #                     response = generate_answer(message, True)
    #                     post_to_channel(event["channel"], response)
    #                 # If mentioning bot
    #                 elif bot_id in message:
    #                     message = message.replace("<@{0}>".format(bot_id), "")
    #                     response = generate_answer(message, False)
    #                     reply_thread(event["ts"], event["channel"], response)

    def html_mrkdwn(self, text):
        text = text.replace('<p>', '').replace('</p>', '')
        text = text.replace('<b>', '*').replace('</b>', '*')
        text = text.replace('<code>', '`').replace('</code>', '`')
        text = text.replace('<pre>', '```').replace('</pre>', '```')
        text = text.replace('<em>', '_').replace('</em>', '_')
        text = text.replace('<strong>', '*').replace('</strong>', '*')
        text = text.replace('````', '```')
        return text

    def generate_answer(self, query, dm=False):
        question = self.helper.get_top_question_from_googlesearch(query)
        response = (
            "404", "404", "Couldn't find a matching question on stackoverflow. Try rephrasing your question.")
        if question is not None:
            answer = self.helper.get_top_answer(question["question_id"])
            response = (question["title"], question["link"],
                        self.html_mrkdwn(answer["body"]))
        return response
