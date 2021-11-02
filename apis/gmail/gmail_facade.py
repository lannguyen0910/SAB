import pickle
import httplib2
import arrow
import sys
import argparse
import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from oauth2client import tools
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from googleapiclient.discovery import build
from oauth2client.client import AccessTokenRefreshError
from configs.config import *


class GmailFacade():
    def __init__(self, token=SLACK_BOT_TOKEN,
                 bot_name=SLACK_BOT_NAME):
        self.token = token
        self.default_channel = DEFAULT_SLACK_CHANNEL
        self.bot_name = bot_name

        # Internally set properites
        self.client = WebClient(token=self.token)
        self.BOT_ID = self.client.api_call("auth.test")['user_id']

        self.icon_emoji = ":robot_face:"

        # Check https://developers.google.com/admin-sdk/directory/v1/guides/authorizing for all available scopes
        OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

        # Location of the credentials storage file
        STORAGE = Storage(GMAIL_STORAGE)

        # Start the OAuth flow to retrieve credentials
        flow = flow_from_clientsecrets(
            GMAIL_CLIENT_SECRET_FILE, scope=OAUTH_SCOPE)
        http = httplib2.Http()

        # Try to retrieve credentials from storage or run the flow to generate them
        parser = argparse.ArgumentParser(parents=[tools.argparser])
        flags = parser.parse_args([])

        credentials = None

        storage = Storage(GMAIL_OAUTH)
        try:
            credentials = storage.get()
        except:
            sys.exit("Unable to retrieve credentials")

        if not credentials:
            credentials = tools.run_flow(flow, STORAGE, flags)

        storage.put(credentials)
        # Authorize the httplib2.Http object with our credentials
        http = credentials.authorize(http)

        # Build the Gmail service from discovery
        self.gmail_service = build('gmail', 'v1', http=http)
        self.user_id = 'me'

        self.label_name = 'INBOX'

        try:
            self.state = pickle.load(
                open(GMAIL_PICKLE, "rb"))
        except IOError:
            self.state = dict()
            self.state['timestamp'] = arrow.utcnow().timestamp

            # self.new_timestamp = arrow.utcnow().timestamp # BUG?  Move to gmail2slack?

    def save_state(self):
        # Save timestamp so we don't process the same files again
        # self.state['timestamp'] = self.new_timestamp
        self.state['timestamp'] = arrow.utcnow().timestamp
        pickle.dump(self.state, open(GMAIL_PICKLE, "wb"))

    def getLabelIdByName(self, name):
        response = self.gmail_service.users().labels().list(userId=self.user_id).execute()
        if "labels" in response:
            for label in response["labels"]:
                if label["name"] == name:
                    return label["id"]
        return None

    def gmail2slack(self, channel_id):
        try:
            label_id = self.getLabelIdByName(self.label_name)
            if not label_id:
                raise Exception("target label name not found")
            response = self.gmail_service.users().messages().list(
                userId=self.user_id, labelIds=label_id).execute()
        except AccessTokenRefreshError:
            return

        message_ids = []
        if 'messages' in response:
            message_ids.extend(response['messages'])

        for msg_id in message_ids:
            message = self.gmail_service.users().messages().get(
                userId=self.user_id, id=msg_id['id']).execute()
            headers = dict()
            for header in message['payload']['headers']:
                headers[header['name']] = header['value']

            try:  # due to issue @ https://github.com/crsmithdev/arrow/issues/176
                from_ts = arrow.get(
                    headers['Date'], 'ddd, D MMM YYYY HH:mm:ss ZZ').timestamp
            except:
                continue

            if from_ts < self.state['timestamp']:
                break
            from_date = arrow.get(from_ts).to(
                'US/Eastern').format('YYYY-MM-DD HH:mm:ss ZZ')
            say = "New Email\n>From: %s\n>Date: %s\n>Subject: %s\n>\n>%s" % \
                  (headers['From'], from_date,
                   headers['Subject'], message['snippet'])

            try:
                self.client.chat_postMessage(
                    text=say, username=self.bot_name, channel=channel_id, icon_emoji=self.icon_emoji)

            except SlackApiError as e:
                logging.error(
                    f"Slack encountered an error: {e.response['error']}")
                raise e

        self.save_state()