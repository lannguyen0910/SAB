# Featured Event       URL -- 'https://api.yelp.com/v3/events/featured'
# Event Search         URL -- 'https://api.yelp.com/v3/events'
# Event Lookup         URL -- 'https://api.yelp.com/v3/events/{id}'

# Import the modules
import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from configs.config import *

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Define an event ID
event_id = 'oakland-saucy-oakland-restaurant-pop-up'

# Define API Key, Search Type, and header
MY_API_KEY = os.environ.get('YELP_API_KEY')
BUSINESS_PATH = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % MY_API_KEY}

# Define the Parameters of the search
# PARAMETERS = {'location': 'San Diego'}

PARAMETERS = {'term': 'ramen',
              'location': 'Berlin' or DEFAULT_LOCATION,
              'open_now': True,
              'limit': DEFAULT_LIMIT}

# Make a Request to the API, and return results
response = requests.get(url=BUSINESS_PATH,
                        params=PARAMETERS,
                        headers=HEADERS)

# Convert response to a JSON String
business_data = response.json()['businesses']

# print the data
print(json.dumps(business_data, indent=3))
