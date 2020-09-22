"""
And Chill Class
===============

Author: Shuo Zhang
"""

from fbchat import Client
from fbchat.models import *
from code.bot.bot import Bot
# from bot import Bot
import time

UID_ANDCHILL = "223760607993718" # https://www.labnol.org/internet/find-facebook-page-id-profile/6909/

class AndChill(Bot):
    # def __init__(self, email="shuo.zhang@uis.no", pswd="33455432"):
    # def __init__(self, email="Radigor_toopa@outlook.com", pswd="topicaloserz"):
    def __init__(self, email="dat640help@gmail.com", pswd="J5GPUksAFPaJJw7"):
        super(Bot, self).__init__()
        self._client = Client(email, pswd)

    def fetch_last_msg(self, text):
        time.sleep(25)
        messages = [i.text for i in self._client.fetchThreadMessages(thread_id=UID_ANDCHILL, limit=20)]
        # print("1", messages)
        if messages[0] != text:
            return [i for i in messages[:messages.index(text)][::-1] if i != ""]
        else:
            return messages[0]
        # if messages[0] != text:
        #     return messages[0]
        # else:
        #     return None

    def generate_response(self, text):
        self.send_message(message=text)
        while True:
            msg = self.fetch_last_msg(text)
            if msg:
                # return "\n".join(msg)
                return msg


    def send_message(self, message):
        """Sends message from tegegram to andchill messenger"""
        self._client.send(Message(text=message), thread_id=UID_ANDCHILL, thread_type=ThreadType.USER)

    def onMessage(self):
        self._client.onMessage()
        messages = self._client.fetchThreadMessages(thread_id=UID_ANDCHILL, limit=1)
        print(messages[0].text)

class Botbot(Bot):
    def __init__(self):
        super(Bot, self).__init__()

    def generate_response(self, text):
        return ""


if "__name__" == "__main__":
    client = AndChill()


