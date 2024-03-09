import json
import logging
import sys
import os.path

from pyChatGPT import ChatGPT
import configargparse


def split_list(list_to_split, n):
    k, m = divmod(len(list_to_split), n)
    return (list_to_split[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


class GPTWrapper:
    token = None
    filepath = None
    chatgpt = None

    logger = None

    kalauer: list[str] = []
    same_kalauer: list[str] = []

    def __init__(self):
        self.logger = logging.getLogger('gpt-wrapper')
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('gpt-wrapper -- [%(funcName)s] %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

        self.logger.debug('Start initializing GPTWrapper')
        self.logger.debug('Parse config')
        self.parse_config()
        self.logger.debug('Parse file')
        self.parse_file()
        self.logger.debug('Start gpt session')
        self.setup_chatgpt()
        self.logger.debug('Start sending messages')
        self.send_messages()
        print(self.same_kalauer)

    def parse_config(self):
        configparser = configargparse.ArgParser()
        configparser.add_argument('-c', '--config', is_config_file=True, help='config file path')
        configparser.add_argument('--token', required=True, help='API Token')
        configparser.add_argument('--file', required=True, help='File to read from')

        self.token = configparser.parse_args().token
        self.filepath = configparser.parse_args().file
        self.logger.debug('Parsed token and file path from config file')

    def parse_file(self):
        if not os.path.exists(self.filepath):
            self.logger.error(f"File {self.filepath} does not exist")
            sys.exit(1)

        if not os.path.isfile(self.filepath):
            self.logger.error(f"{self.filepath} is not a file")
            sys.exit(1)

        with open(self.filepath, 'r', encoding='utf-8') as file:
            self.logger.debug('Opened file')
            data = json.load(file)
            data = data['users']

            self.logger.debug('Go through data and add to list')
            for user, user_data in data.items():
                records = user_data['record']
                self.logger.debug(f'User {user} has {len(records)} records')
                for record in records:
                    self.kalauer.append(record['text'])
            self.logger.debug(f'Saved all data to list, saved {len(self.kalauer)} records')

    def setup_chatgpt(self):
        self.chatgpt = ChatGPT(self.token, moderation=False, chrome_args=['--no-sandbox', '--disable-dev-shm-usage'])

    def send_messages(self):
        i = 0
        print(self.kalauer)
        for record in self.kalauer:
            cross_check = False
            other_records_list = self.kalauer.copy()
            other_records_list.remove(record)
            splitted_records = list(split_list(other_records_list, 5))
            self.logger.debug(f"Split records into {len(splitted_records)} parts")
            for other_records in splitted_records:
                other_records = '\n'.join(other_records)
                message = "Ich habe hier folgenden Witz: \"" + record + "\". Ist dieser Witz inhaltlich gleich zu irgendeinem anderen der folgenden Witze? Antworte mit Ja oder Nein.\n" + other_records
                resp = self.chatgpt.send_message(message)
                self.chatgpt.reset_conversation()
                if "Ja" in resp['message']:
                    cross_check = True
                    break
            self.logger.debug(
                f"Cross-Check for message {self.kalauer.index(record) + 1}/{len(self.kalauer)}: {cross_check}")
            if cross_check:
                self.same_kalauer.append(record)
            i += 1
            if i > 10:
                break


if __name__ == "__main__":
    GPTWrapper()
