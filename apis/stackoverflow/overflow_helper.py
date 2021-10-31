import urllib
import requests
from bs4 import BeautifulSoup
import html
# from fake_useragent import UserAgent
from googlesearch import Search
import json


class OverflowHelper():
    """
    Helper class for searching from Stackoverflow's answer
    """

    def __init__(self):
        self.stackoverflow_base_api = "https://api.stackexchange.com/2.3"
        self.time_delay = 5

    # Uses Top Stackoverflow search results on Google Search.
    def get_top_question_from_googlesearch(self, question, num_results=100):
        search_results = Search(query=question, number_of_results=num_results)

        for result in search_results.results:
            # In case, the first search result isn't on stackoverflow, we search until we find one or reach end of results.
            if "https://stackoverflow.com/questions/" in result.url:
                # Grab the question id from the link
                question_id = result.url.replace(
                    "https://stackoverflow.com/questions/", "").split("/")[0]
                return {
                    "title": result.title,
                    "link": result.url,
                    "question_id": question_id,
                }
        # Found nothing
        return None

    def get_top_answer(self, question_id):
        answer_request = requests.get(
            url="{0}/questions/{1}/answers".format(
                self.stackoverflow_base_api, str(question_id)),
            params={
                "order": "desc",
                "sort": "votes",
                "site": "stackoverflow",
                "filter": "withbody"
            },
            headers={
                "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
            }
        )

        answer_response = answer_request.json()
        top_answer = answer_response['items'][0]

        return top_answer

    def get_top_question_from_stackoverflow(self, question, num_of_results=5):
        question_request = requests.get(
            url="{0}/search/advanced".format(self.stackoverflow_base_api),
            params={
                "order": "desc",
                "sort": "votes",
                "q": question,
                "site": "stackoverflow"
            }
        )

        question_response = question_request.json()
        top_questions = question_response["items"][:num_of_results]

        # print(json.dumps(top_questions, indent=4, sort_keys=True))
        question_ids, titles, links = [], [], []
        for question in top_questions:
            question_ids.append(question['question_id'])
            links.append(question['link'])
            titles.append(question['title'])

        return question_ids, titles, links


if __name__ == '__main__':
    helper = OverflowHelper()
    question = "How to loop through a list of dict"
    # question_id=helper.get_top_question(question)
    top_question = helper.get_top_question_from_googlesearch(question)
    print('Id: ', top_question['question_id'])
    print(helper.get_top_answer(top_question['question_id']))
