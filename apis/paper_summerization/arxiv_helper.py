import arxiv
import re

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


class ArxivHelper:
    # constants
    def __init__(self):
        self.ARXIV_REGEX = r'(https?://[^\s]+[0-9]+)'

        # for sumy
        self.lang = 'english'
        self.tknz = Tokenizer(self.lang)
        self.stemmer = Stemmer(self.lang)
        self.summarizer = Summarizer(self.stemmer)

    def summarize(self, string, num_sentence=3):
        """
        Summarize a sentence with sumy
        """
        parser = PlaintextParser(string, self.tknz)
        parser.stop_word = get_stop_words(self.lang)
        summ_string = ''
        for sentence in self.summarizer(parser.document, num_sentence):
            summ_string += str(sentence) + ' '
        return summ_string

    def parse_arxiv_link(self, command):
        """
        Hacky way to parse out an an arxiv ID from a sentence
        """
        links = re.findall(self.ARXIV_REGEX, command)
        print('Links: ', links)
        arxiv_ids = []
        if len(links) > 0:
            for link in links:
                print(link)
                if 'arxiv' not in link:
                    continue
                arxiv_id = link.split('/')[-1]
                arxiv_id = arxiv_id.split('.pdf')[0]
                arxiv_ids.append(arxiv_id)

        articles = []
        if len(arxiv_ids) > 0:
            articles = list(arxiv.Search(id_list=arxiv_ids).results())
        else:
            command = command.split(', ')
            query = command[0]

            sort_type = None
            default_sort = arxiv.SortCriterion.Relevance
            sort_dict = {'relevance': arxiv.SortCriterion.Relevance,
                         'subdate': arxiv.SortCriterion.SubmittedDate,
                         'lastupdate': arxiv.SortCriterion.LastUpdatedDate}

            if len(command) == 2:
                sort_type = command[1].lower()

            if sort_type not in sort_dict.keys():
                final_sort = default_sort
            else:
                final_sort = sort_dict[sort_type]

            articles = list(arxiv.Search(
                query=query, max_results=5, sort_by=final_sort).results())

        return articles

    def format_arxiv(self, article, do_summarize=True):
        """
        Format an arxiv article info into a response string
        Optionally summarize the abstract with sumy
        """
        msg = 'Title: %s\n' % article.title
        authors = [a.name for a in article.authors]
        msg += 'Authors: %s\n' % ', '.join(authors)
        abstract = ' '.join(article.summary.split('\n'))
        if do_summarize:
            abstract = self.summarize(abstract)
        msg += '\nAbstract (auto-summarized): ' + abstract + '\n\n'
        msg += 'PDF: %s' % article.pdf_url
        return msg


if __name__ == '__main__':
    helper = ArxivHelper()

    command = '$arxiv search https://arxiv.org/abs/1710.01813'

    articles = helper.parse_arxiv_link(command)
    print('Articles: ', articles)
    for article in articles:
        msg = helper.format_arxiv(article)
        print('Msg: ', msg)
        print('\n')
