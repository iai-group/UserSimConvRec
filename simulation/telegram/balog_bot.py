"""
BalogBot class
==============

https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay

Author: Shuo Zhang
"""

import json
import requests
import time
import urllib
from simulation.telegram.dbhelper import DBHelper
from simulation.telegram import TOKEN, URL

db = DBHelper()


class BalogBot:
    def __init__(self):
        db.setup()

    @staticmethod
    def get_url(url):
        """Downloads the content from a URL and returns a string"""
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        """Gets the string response and parses it into a Python dictionary """
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def get_updates(self, offset=None):
        """Calls the API and retrieves a list of updates"""
        url = URL + "getUpdates"
        if offset:
            url += "?offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js

    @staticmethod
    def get_last_update_id(updates):
        """Gets the last chat ID"""
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    def handle_updates(self, updates):
        for update in updates["result"]:
            text = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            items = db.get_items(chat)
            if text == "/done":
                keyboard = self.build_keyboard(items)
                self.send_message("Select an item to delete", chat, keyboard)
            elif text == "/start":
                self.send_message(
                    "Welcome to your personal To Do list. Send any text to me and I'll store it as an item. Send /done to remove items",
                    chat)
            elif text.startswith("/"):
                continue
            elif text in items:
                db.delete_item(text, chat)
                items = db.get_items(chat)
                keyboard = self.build_keyboard(items)
                self.send_message("Select an item to delete", chat, keyboard)
            else:
                db.add_item(text, chat)
                items = db.get_items(chat)
                message = "\n".join(items)
                self.send_message(message, chat)

    @staticmethod
    def get_last_chat_id_and_text(updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return (text, chat_id)

    @staticmethod
    def build_keyboard(items):
        keyboard = [[item] for item in items]
        reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
        return json.dumps(reply_markup)

    def send_message(self, text, chat_id, reply_markup=None):
        text = urllib.parse.quote_plus(text)
        url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
        if reply_markup:
            url += "&reply_markup={}".format(reply_markup)
        self.get_url(url)


def main():
    bb = BalogBot()
    last_update_id = None
    while True:
        updates = bb.get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = bb.get_last_update_id(updates) + 1
            bb.handle_updates(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()
