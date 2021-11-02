import requests
import logging
import pandas as pd
import os
import matplotlib.pyplot as plt
from utils import tableize
plt.switch_backend('agg')

def pretty_format(dict, mapping_dict=None, index=False):
    if mapping_dict is None:
        mapping_dict = {key:key for key in list(dict.keys())}

    new_dict = {mapping_dict[key]:[value] for key, value in dict.items() if key in mapping_dict.keys()}

    print('New dict: ', new_dict)

    plot_image(new_dict)

    df = pd.DataFrame(new_dict)

    pd.set_option('display.max_columns', None)  # or 1000
    pd.set_option('display.max_rows', None)  # or 1000
    pd.set_option('display.max_colwidth', None)  # or 199

    return tableize(df)

def plot_image(info):
    if 'Slug' not in info.keys():
        info['Slug'] = 'global'
        info['Country'] = 'World'

    plt.bar(info['Country'], info['Confirmed'], color= 'red', label= 'New Cases')
    plt.bar(info['Country'], info['Recovered'], color= 'blue', label= 'New Recovered')
    plt.bar(info['Country'], info['Deaths'], color= 'black', label= 'New Deaths')

    plt.legend()

    plt.savefig(f'images/{"".join(info["Slug"])}.png')

class CovidApiHelper:
    def __init__(self):
        self.url = "https://api.covid19api.com/"
    
    def send_request(self, url, data, type, headers, **kwargs):
        if type == 'post':
            response = requests.post(url, data=data, headers=headers)
        elif type == 'get':
            response = requests.get(url, data=data, headers=headers)

        return self.process_response(response, **kwargs)
    
    def process_response(self, response, country_name):
        """
        Process response from server
        """
        try:
            data = response.json()  
            if 'message' not in data.keys():

                if country_name == 'global':
                    covid_info = data["Global"] # a dict

                    """
                    "NewConfirmed": 100282,
                    "TotalConfirmed": 1162857,
                    "NewDeaths": 5658,
                    "TotalDeaths": 63263,
                    "NewRecovered": 15405,
                    "TotalRecovered": 230845
                    """

                    extracted_keys = {
                      "TotalConfirmed": "Confirmed",
                      "TotalDeaths": "Deaths",
                      "TotalRecovered": "Recovered"
                    }
                else:
                    countries_info = data["Countries"] # a list of dict

                    """
                    "Country": "Viet Nam",
                    "CountryCode": "VN",
                    "Slug": "vietnam",
                    "NewConfirmed": 3,
                    "TotalConfirmed": 240,
                    "NewDeaths": 0,
                    "TotalDeaths": 0,
                    "NewRecovered": 5,
                    "TotalRecovered": 90,
                    "Date": "2020-04-05T06:37:00Z"
                    """

                    extracted_keys = {
                      "Country": "Country",
                      "TotalConfirmed": "Confirmed",
                      "TotalDeaths": "Deaths",
                      "TotalRecovered": "Recovered",
                      "Slug": "Slug"
                    }

                    covid_info = {}
                    for country in countries_info:
                        if country['Slug'] == country_name:
                            covid_info = country
                            break
                

                response = pretty_format(covid_info, extracted_keys)           
            else:
                logging.info(f"Bad request code...")
                response = f"[Error] Request code {data['code']}"
                return               
        except Exception as e:
            logging.info(f"Error...")
            response = "[Error] " + str(e)

        return response

    def get_summary(self, country_name):
        """
        Main method to send request and return buffer of result image
        Countries Names - Check out Slug from: https://api.covid19api.com/countries
        """
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        url = os.path.join(self.url, 'summary')

        if country_name == '':
            country_name = 'global'

        payload = {}

        # Send request
        response = self.send_request(url, payload, type='get', headers=headers, country_name=country_name)
        
        logging.info(f"Received response from {self.url}")
        return response

if __name__ == '__main__':
    covid = CovidApiHelper()
    summary = covid.get_summary('united-states')
    
    print(summary)