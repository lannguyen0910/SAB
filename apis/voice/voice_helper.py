import os
from gtts import gTTS
from googletrans import Translator


CACHE_DIR ='./.cache'

def find_text(text):  
    """
    Find string inside double quotes    
    """
    import re
    matches=re.findall(r'\"(.+?)\"',text)
    return matches[0]

class GoogleVoiceHelper:
    """
    Google Text-To-Speech API
    https://github.com/pndurette/gTTS
    """
    translator = Translator()
    def __init__(self) -> None:
        super().__init__()
        self.triggers = ["$speak"]

    @staticmethod
    def speak(text, lang=None):
        """
        Convert text to speech, save to mp3 and convert to Discord player
        """
        if not os.path.exists(CACHE_DIR):
            os.mkdir(CACHE_DIR)
        filename = os.path.join(CACHE_DIR, "temp.mp3")

        if lang is None:
            # Detect language
            lang = GoogleVoiceHelper.translator.detect(text).lang

        # Saving the converted audio in a mp3 file
        speech = gTTS(text=text, lang=lang, slow=False)

        # Save to cache folder
        speech.save(filename)

        if os.path.exists(filename):
            print('Sucessfully created speech!')
        else:
            print('Error...')

    def do_command(self, command, lang='vi'):
        """
        Execute command
        """
        text = find_text(command) # find texts in double quotes
        self.speak(text, lang)   


if __name__ == '__main__':
    helper = GoogleVoiceHelper()
    text = '$speak "Thực ra là mình đã mến bạn từ rất lâu rồi đấy :>"'
    lang = 'vi'

    helper.do_command(text, lang)
