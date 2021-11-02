import logging
import time
import traceback
from apis.covid19.covid_facade import CovidFacade
from apis.covid19.covid_helper import CovidApiHelper

from apis.news.news_helper import NewsApiHelper
from apis.news.news_facade import NewsFacade
from apis.news.query_helper import QueryHelper

from apis.translate.translate_helper import TranslateHelper
from apis.translate.translate_facade import TranslateFacade

from apis.location_search.location_search_helper import LocationSearchHelper
from apis.location_search.location_search_facade import LocationSearchFacade

from apis.wiki_search.wiki_search_helper import WikiHelper
from apis.wiki_search.wiki_search_facade import WikiFacade

# from apis.gmail.gmail_facade import GmailFacade

from apis.stackoverflow.overflow_facade import OverflowFacade

from apis.voice.voice_helper import GoogleVoiceHelper
from apis.voice.voice_facade import VoiceFacade

# from apis.text_generation.gpt2_facade import GPT2Facade

from configs.config import *
from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
from utils import *


app = Flask(__name__)

# Create an events adapter and register it to an endpoint in the slack app for event injestion.
slack_event_adapter = SlackEventAdapter(
    os.environ['SIGNING_SECRET'], '/slack/events', app)

# Set up logging.
logging.basicConfig(
    # filename=config.LOGFILE,
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

news_api_helper = NewsApiHelper()
news_facade = NewsFacade()

covid_api_healper = CovidApiHelper()
covid_facade = CovidFacade()

translate_api_helper = TranslateHelper()
translate_facade = TranslateFacade()

location_search_helper = LocationSearchHelper()
location_search_facade = LocationSearchFacade()

wiki_helper = WikiHelper()
wiki_facade = WikiFacade()

# gmail_facade = GmailFacade()

overflow_facade = OverflowFacade()

voice_helper = GoogleVoiceHelper()
voice_facade = VoiceFacade()


@slack_event_adapter.on('message')
# Handle all message events
def handle_message(payload):
    # payload is all the information from the API
    event = payload.get('event', {})
    user_id = event.get('user')
    channel_id = event.get('channel')
    text = event.get('text')

    default_message = "I'm sorry. I don't understand."

    if event.get('bot_id') is None and user_id != None and news_facade.BOT_ID != user_id:
        if text.lower() == 'hello' or text.lower() == 'hi':
            response = show_commands(user_id)
            news_facade.client.chat_postMessage(channel=channel_id, **response)

        elif "$news" in text[:5].lower():
            user_response = text[5:].split(", ")
            category = None

            category = user_response[0]
            print("Category: ", category)

            country = user_response[1] if len(user_response) > 1 else None
            language = user_response[2] if len(user_response) > 2 else None
            query = user_response[3] if len(user_response) > 3 else None

            query_helper = QueryHelper(query=query,
                                       category=category,
                                       country=country,
                                       language=language,
                                       slack_channel=channel_id)

            result = news_api_helper.get_top_headlines(query_helper)
            logging.info(f"Retrieved {result['totalResults']} results.")
            articles = result["articles"]

            news_facade.send_messages(
                articles,
                name="Hot News",
                channel=channel_id
            )

            return Response(), 200

        elif "$covid" in text[:6].lower():
            user_response = text[7:].split(", ")
            countries = []
            if len(user_response) == 0:
                country = 'global'
                countries.append(country)
            else:
                for i in range(0, len(user_response)):
                    countries.append(str(user_response[i]))

            print('Countries: ', countries)

            responses, files = [], []
            for country in countries:
                response = covid_api_healper.get_summary(country)
                responses.append(response)
                files.append(f'./images/{country}.png')

            logging.info(
                f"Retrieved {len(responses)} responses from {len(countries)} countries.")

            covid_facade.send_messages(
                responses,
                files,
                channel=channel_id
            )

            return Response(), 200

        elif '$translate' in text[:10].lower():
            user_response = text[11:].split(", ")

            # language you want translate to
            assigned_language = user_response[0]
            # text of any languages that you want to translate
            text = user_response[1]

            language_code = DEFAULT_LANGUAGE_CODE
            for language_tuple in LANGUAGES:
                if language_tuple[1].lower() == assigned_language:
                    language_code = language_tuple[0]
            
            response = translate_api_helper.do_command(text, language_code)

            translate_facade.send_messages(response, channel=channel_id)

            return Response(), 200

        elif "$search" in text[:7].lower():
            user_response = text[8:].split(", ")
            location = None
            if len(user_response) > 1:
                location = user_response[1]

            term = user_response[0]
            result = location_search_helper.search(term, location)

            location_search_facade.send_messages(
                result, location, channel=channel_id)

            return Response(), 200

        elif '$wiki' in text[:5].lower():
            user_response = text[6:].split(", ")

            # language you want translate to
            assigned_language = user_response[0]
            # text of any languages that you want to translate
            text = user_response[1]

            language_code = DEFAULT_LANGUAGE_CODE
            for language_tuple in LANGUAGES:
                if language_tuple[1].lower() == assigned_language:
                    language_code = language_tuple[0]

            response = wiki_helper.do_command(text, language_code)

            wiki_facade.send_messages(response, channel=channel_id)

            return Response(), 200

        # elif '$gpt2' in text[:5].lower():
        #     query = text[6:]
        #     print('Gpt2 query: ', query)
        #     gpt2_facade.send_messages(query, channel=channel_id)

        #     return Response(), 200

        elif '$overflow' in text[:9].lower():
            query = text.split('overflow')[-1].lstrip().rstrip()
            print('Overflow query: ', query)
            overflow_facade.send_messages(query, channel=channel_id)

            return Response(), 200

        # elif '$gmail' in text[:6].lower():
        #     user_response = text.split(' ')
        #     while True:
        #         try:
        #             gmail_facade.gmail2slack(channel_id=channel_id)
        #         except:
        #             traceback.print_exc()

        #         if len(user_response) != 1 and user_response[1].lower() == 'stop':
        #             break

        #         time.sleep(10)

        #     return Response(), 200
            
        elif "$voice" in text[:6].lower():
            user_response = text[7:].split(", ")

            # language you want translate to
            assigned_language = user_response[0]
            # text of any languages that you want to translate
            text = user_response[1]

            language_code = DEFAULT_LANGUAGE_CODE
            for language_tuple in LANGUAGES:
                if language_tuple[1].lower() == assigned_language:
                    language_code = language_tuple[0]
            
            print("language_code: " + language_code)

            voice_helper.do_command(text, lang=language_code)

            filename = './.cache/temp.mp3'

            voice_facade.send_messages(filename, channel=channel_id)

            return Response(), 200

        else:   
            news_facade.client.chat_postMessage(
                channel=channel_id, text=default_message)

            response = show_commands(user_id)
            news_facade.client.chat_postMessage(channel=channel_id, **response)


if __name__ == "__main__":
    app.run(debug=True)
