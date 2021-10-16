import logging
from apis.covid19.covid_facade import CovidFacade
from apis.covid19.covid_helper import CovidApiHelper

from apis.news.news_helper import NewsApiHelper
from apis.news.news_facade import NewsFacade
from apis.news.query_helper import QueryHelper

from apis.translate.translate_helper import TranslateHelper
from apis.translate.translate_facade import TranslateFacade


from configs.config import *
from flask import Flask, Response
from slackeventsapi import SlackEventAdapter
from dotenv import load_dotenv
from pathlib import Path
from utils import *



env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

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

@slack_event_adapter.on('message')
# Handle all message events
def handle_message(payload):
    # payload is all the information from the API
    event = payload.get('event', {})
    user_id = event.get('user')
    channel_id = event.get('channel')
    text = event.get('text')


    default_message = "I'm sorry. I don't understand."

    if user_id != None and news_facade.BOT_ID != user_id:
        if text.lower() == 'hello' or text.lower() == 'hi':
            response = show_commands(user_id)
            news_facade.client.chat_postMessage(channel=channel_id, **response)

        elif "/news" in text[:5].lower():
            user_response = text[5:].split(", ")
            category = None

            category = user_response[0]
            print("Category: ", category)

            country = user_response[1] if len(user_response) > 1 else None
            language = user_response[2] if len(user_response) > 2 else None
            query = user_response[3]  if len(user_response) > 3 else None

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
        
        elif "/covid" in text[:6].lower():
            user_response = text[6:].split(", ")
            countries = []
            if len(user_response) == 0:
                country = 'global'
                countries.append(country)
            else:
                for i in range(1, len(user_response)):
                    countries.append(str(user_response[i]))
            
            print('Countries: ', countries)

            responses, files = [], []
            for country in countries:
                response = covid_api_healper.get_summary(country)
                responses.append(response)
                files.append(f'./images/{country}.png')
            logging.info(f"Retrieved {len(responses)} responses from {len(countries)} countries.")

            covid_facade.send_messages(
                responses, 
                files, 
                channel=channel_id
            )

            return Response(), 200

        elif '/translate' in text[:10].lower():
            user_response = text[10:].split(", ")

            assigned_language = user_response[0] # language you want translate to
            text = user_response[1] # text of any languages that you want to translate

            language_code = DEFAULT_LANGUAGE_CODE
            for language_tuple in LANGUAGES:
                if language_tuple[1] == assigned_language:
                    language_code = language_tuple[0]

            response = translate_api_helper.do_command(text, language_code)

            translate_facade.send_messages(response, channel=channel_id)


            return Response(), 200


        else:
            news_facade.client.chat_postMessage(
                channel=channel_id, text=default_message)

            response = show_commands(user_id)
            news_facade.client.chat_postMessage(channel=channel_id, **response)

if __name__ == "__main__":
    app.run(debug=True)
