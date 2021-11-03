import wikipedia
import logging


class WikiHelper:
    """
    Search query from wikipedia
    https://github.com/goldsmith/Wikipedia
    """

    def __init__(self) -> None:
        super().__init__()

    def do_command(self, command, language_code='en'):
        """
        Execute command
        """

        wikipedia.set_lang(language_code)
        # Ex: wikipedia.set_lang("vi")

        response = None

        # Example call: #wiki python programming
        query = command.split('wiki')[-1].lstrip().rstrip()

        try:
            response = wikipedia.summary(query, sentences=5)
            logging.info(f'{response}')

        except wikipedia.exceptions.DisambiguationError as e:
            response = "Try one of these options: \n"
            for idx, opt in enumerate(e.options[:5]):
                response += f"{idx}. {opt}\n"
            logging.error(f'{response}')

        except wikipedia.exceptions.PageError as e:
            response = f"{query} not found on Wikipedia"
            logging.error(f'{response}')

        return response


if __name__ == '__main__':
    wiki = WikiHelper()
    text = ' /wiki python programming'
    response = wiki.do_command(text, 'vi')
    print(response)
