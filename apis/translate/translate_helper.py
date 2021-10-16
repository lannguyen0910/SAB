from googletrans import Translator
import logging

def find_text(text):  
    """
    Find string inside double quotes    
    """
    import re
    matches=re.findall(r'\"(.+?)\"',text)
    return matches[0]

class TranslateHelper:
    """
    Google translation API
    https://py-googletrans.readthedocs.io/en/latest/
    """
    def __init__(self) -> None:
        super().__init__()
        self.translator = Translator()

    def do_command(self, command, dest):
        """
        Execute command
        """
        response = None

        # command ex: /translate "Hello"
        try:
            text = find_text(command) # find texts in double quotes
            response = self.translate(text=text, dest=dest)

            logging.info(f"{response}")
            return response
        except Exception as e:
            response = "[Error] " + str(e)
            logging.error(f'{response}')

        return response

    def detect_language(self, text):
        """
        Detect text's language
        """
        result = self.translator.detect(text)
        lang = result.lang

        logging.info(f'Detected language: {lang}')
        return lang

    def translate(self, text, src=None, dest='vi'):
        """
        Translate a text
        """
        if src is None:
            src = self.detect_language(text)

        result = self.translator.translate(text,src=src, dest=dest)
        response = result.text

        logging.info(f'Translated text: {response}')
        return response

if __name__ == '__main__':
    google = TranslateHelper()
    text = '/translate "I love you"'
    response = google.do_command(text, 'vi')
    print("Response: ", response)
    
