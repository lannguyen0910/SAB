import logging
import requests
from configs.config import *


class LocationSearchHelper:
    def __init__(self):
        self.search_api_url = 'https://api.yelp.com/v3/businesses/search'
        self.header =  {
            'Authorization': 'Bearer %s' % YELP_API_KEY,
        }
    
    def search(self, term, location):
        params = {
            'term': term,
            'location': location or DEFAULT_LOCATION,
            'open_now': True,
            'limit': DEFAULT_LIMIT
        }

        try:
            response = requests.get(self.search_api_url, headers=self.headers, params=params)
            logging.info(f'Response json: {response.json()}')

            return response.json()['businesses']
        except Exception as e:
            response = "[Error] " + str(e)
            logging.error(f'{response}')
        
        return response