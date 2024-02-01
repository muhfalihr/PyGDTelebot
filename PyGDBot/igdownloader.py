import io
import os
import re
import json
import telebot
import logging
import inspect
import hashlib

from requests.sessions import Session
from telebot import types
from urllib.parse import quote
from datetime import datetime
from PyGDBot.logger import setup_logging
from PyGDBot.exception import *
from PyGDBot.html_parser import HtmlParser
from faker import Faker
from typing import Any
from dotenv import load_dotenv


class PyGDTelebot:
    def __init__(self) -> Any:
        load_dotenv()

        TOKEN = os.environ.get("TELEBOT_TOKEN")
        self.__bot = telebot.TeleBot(token=TOKEN)

        self.__cookie = os.environ.get("IG_COOKIE")

        self.__parser = HtmlParser()
        self.__session = Session()
        self.__fake = Faker()

        setup_logging()
        self.__logger = logging.getLogger(self.__class__.__name__)

        self.__headers = dict()
        self.__headers["Accept"] = "application/json, text/plain, */*"
        self.__headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.__headers["Sec-Fetch-Dest"] = "empty"
        self.__headers["Sec-Fetch-Mode"] = "cors"
        self.__headers["Sec-Fetch-Site"] = "same-site"
        self.__headers["Cookie"] = self.__cookie

        self.__current_func = lambda: inspect.getouterframes(
            inspect.currentframe()
        )[1][3]
        self.__hashmd5 = lambda url: hashlib.md5().update(url.encode("utf-8")).hexdigest()

        @self.__bot.message_handler(commands=["start", "hello"])
        def instruction(message):
            id = message.chat.id
            username = message.from_user.username

            self.__bot.reply_to(
                message=message,
                text=f"Welcome👋, {username}"
            )
            self.__bot.send_message(
                chat_id=id,
                text=(
                    "Instructions for use:\n"
                    "  - /allmedia username=username count=33 max_id=abcdefghij\n"
                    "  - /images username=username count=33 max_id=abcdefghij\n"
                    "  - /videos username=username count=33 max_id=abcdefghij\n"
                    "  - /linkdownloader https://www.instagram.com/p/code/?utm_source=ig_web_copy_link\n\n"
                    "Explanation:\n"
                    "  - username (Required)\n"
                    "  - count (Optional) Default = 33\n"
                    "  - max_id (Optional) Used to retrieve the next media.\n"
                )
            )

        @self.__bot.message_handler(commands=["allmedia", "am"])
        def send_allmedia(message):
            id = message.chat.id
            parameters = dict()

            for param in message.text.split():
                if "=" in param:
                    parameter = param.split("=")
                    parameters.update({parameter[0]: parameter[1]})

            if parameters:
                self.__bot.reply_to(
                    message=message,
                    text="Please wait...\nStill contains a lot of media."
                )
                medias, max_id = self.allmedia(**parameters)

                media_group = []

                for media in medias:
                    data, filename, content_type = self.__download(media)

                    databyte = io.BytesIO(data)
                    databyte.name = filename

                    if len(media_group) == 10:
                        media_group.clear()

                    if len(media_group) < 10:
                        if "image" in content_type:
                            media_group.append(
                                types.InputMediaPhoto(media=databyte)
                            )
                        elif "video" in content_type:
                            media_group.append(
                                types.InputMediaVideo(media=databyte)
                            )

                    if len(media_group) == 10:
                        self.__bot.send_media_group(
                            chat_id=id,
                            media=media_group
                        )

                self.__bot.send_message(
                    chat_id=id, text=f"Max ID for next media = {max_id}")
            else:
                self.__bot.send_message(
                    chat_id=id, text=f"Your command is not correct.")
                self.__bot.send_message(
                    chat_id=id,
                    text=(
                        "Instructions for use:\n"
                        "  - /allmedia username=username count=33 max_id=abcdefghij\n"
                        "  - /images username=username count=33 max_id=abcdefghij\n"
                        "  - /videos username=username count=33 max_id=abcdefghij\n"
                        "  - /linkdownloader https://www.instagram.com/p/code/?utm_source=ig_web_copy_link\n\n"
                        "Explanation:\n"
                        "  - username (Required)\n"
                        "  - count (Optional) Default = 33\n"
                        "  - max_id (Optional) Used to retrieve the next media.\n"
                    )
                )

        @self.__bot.message_handler(commands=["images", "imgs"])
        def send_images(message):
            id = message.chat.id
            parameters = dict()

            for param in message.text.split():
                if "=" in param:
                    parameter = param.split("=")
                    parameters.update({parameter[0]: parameter[1]})

            if parameters:
                self.__bot.reply_to(
                    message=message,
                    text="Please wait...\nStill loading the images."
                )
                medias, max_id = self.images(**parameters)

                media_group = []

                for media in medias:
                    data, filename, content_type = self.__download(media)

                    databyte = io.BytesIO(data)
                    databyte.name = filename

                    if len(media_group) == 10:
                        media_group.clear()

                    if len(media_group) < 10:
                        media_group.append(
                            types.InputMediaPhoto(media=databyte)
                        )

                    if len(media_group) == 10:
                        self.__bot.send_media_group(
                            chat_id=id,
                            media=media_group
                        )

                self.__bot.send_message(
                    chat_id=id, text=f"Max ID for next media = {max_id}")
            else:
                self.__bot.send_message(
                    chat_id=id, text=f"Your command is not correct.")
                self.__bot.send_message(
                    chat_id=id,
                    text=(
                        "Instructions for use:\n"
                        "  - /allmedia username=username count=33 max_id=abcdefghij\n"
                        "  - /images username=username count=33 max_id=abcdefghij\n"
                        "  - /videos username=username count=33 max_id=abcdefghij\n"
                        "  - /linkdownloader https://www.instagram.com/p/code/?utm_source=ig_web_copy_link\n\n"
                        "Explanation:\n"
                        "  - username (Required)\n"
                        "  - count (Optional) Default = 33\n"
                        "  - max_id (Optional) Used to retrieve the next media.\n"
                    )
                )

        @self.__bot.message_handler(commands=["videos", "vds"])
        def send_videos(message):
            id = message.chat.id
            parameters = dict()

            for param in message.text.split():
                if "=" in param:
                    parameter = param.split("=")
                    parameters.update({parameter[0]: parameter[1]})

            if parameters:
                self.__bot.reply_to(
                    message=message,
                    text="Please wait...\nStill loading the videos."
                )
                medias, max_id = self.videos(**parameters)

                media_group = []

                for media in medias:
                    data, filename, content_type = self.__download(media)

                    databyte = io.BytesIO(data)
                    databyte.name = filename

                    if len(media_group) == 3:
                        media_group.clear()

                    if len(media_group) < 3:
                        media_group.append(
                            types.InputMediaVideo(media=databyte)
                        )

                    if len(media_group) == 3:
                        self.__bot.send_media_group(
                            chat_id=id,
                            media=media_group
                        )

                if media_group:
                    self.__bot.send_media_group(
                        chat_id=id,
                        media=media_group
                    )

                self.__bot.send_message(
                    chat_id=id, text=f"Max ID for next media = {max_id}")
            else:
                self.__bot.send_message(
                    chat_id=id, text=f"Your command is not correct.")
                self.__bot.send_message(
                    chat_id=id,
                    text=(
                        "Instructions for use:\n"
                        "  - /allmedia username=username count=33 max_id=abcdefghij\n"
                        "  - /images username=username count=33 max_id=abcdefghij\n"
                        "  - /videos username=username count=33 max_id=abcdefghij\n"
                        "  - /linkdownloader https://www.instagram.com/p/code/?utm_source=ig_web_copy_link\n\n"
                        "Explanation:\n"
                        "  - username (Required)\n"
                        "  - count (Optional) Default = 33\n"
                        "  - max_id (Optional) Used to retrieve the next media.\n"
                    )
                )

        @self.__bot.message_handler(commands=["linkdownloader", "ld"])
        def send_media_from_ld(message):
            id = message.chat.id
            param = ""

            pattern = r'https:\/\/www\.instagram\.com\/.+\/.+\/\?utm_source=ig_web_copy_link'

            try:
                param = message.text.split()[1]

                if re.match(pattern=pattern, string=param):
                    self.__bot.reply_to(
                        message=message,
                        text="Please wait...\nStill loading the media."
                    )
                    medias = self.linkdownloader(param)

                    media_group = []

                    for media in medias:
                        data, filename, content_type = self.__download(media)

                        databyte = io.BytesIO(data)
                        databyte.name = filename

                        if len(media_group) == 10:
                            media_group.clear()

                        if len(media_group) < 10:
                            if "image" in content_type:
                                media_group.append(
                                    types.InputMediaPhoto(media=databyte)
                                )
                            elif "video" in content_type:
                                media_group.append(
                                    types.InputMediaVideo(media=databyte)
                                )

                        if len(media_group) == 10:
                            self.__bot.send_media_group(
                                chat_id=id,
                                media=media_group
                            )

                    if media_group:
                        self.__bot.send_media_group(
                            chat_id=id,
                            media=media_group
                        )

                    self.__bot.send_message(
                        chat_id=id, text="Media download is complete.")
                else:
                    self.__bot.send_message(
                        chat_id=id, text=f"Your command is not correct.")
                    self.__bot.send_message(
                        chat_id=id,
                        text=(
                            "Instructions for use:\n"
                            "  - /allmedia username=username count=33 max_id=abcdefghij\n"
                            "  - /images username=username count=33 max_id=abcdefghij\n"
                            "  - /videos username=username count=33 max_id=abcdefghij\n"
                            "  - /linkdownloader https://www.instagram.com/p/code/?utm_source=ig_web_copy_link\n\n"
                            "Explanation:\n"
                            "  - username (Required)\n"
                            "  - count (Optional) Default = 33\n"
                            "  - max_id (Optional) Used to retrieve the next media.\n"
                        )
                    )

            except IndexError:
                self.__bot.send_message(
                    chat_id=id, text=f"Your command is not correct.")
                self.__bot.send_message(
                    chat_id=id,
                    text=(
                        "Instructions for use:\n"
                        "  - /allmedia username=username count=33 max_id=abcdefghij\n"
                        "  - /images username=username count=33 max_id=abcdefghij\n"
                        "  - /videos username=username count=33 max_id=abcdefghij\n"
                        "  - /linkdownloader https://www.instagram.com/p/code/?utm_source=ig_web_copy_link\n\n"
                        "Explanation:\n"
                        "  - username (Required)\n"
                        "  - count (Optional) Default = 33\n"
                        "  - max_id (Optional) Used to retrieve the next media.\n"
                    )
                )

    def __Csrftoken(self) -> str:
        self.__logger.info("Retrieves X-Csrf-Token from cookie.")

        pattern = re.compile(r'csrftoken=([a-zA-Z0-9_-]+)')
        matches = pattern.search(self.__cookie)
        if matches:
            csrftoken = matches.group(1)
            return csrftoken
        else:
            self.__logger.error(
                CSRFTokenMissingError(
                    "Error! CSRF token is missing. Please ensure that a valid CSRF token is included in the cookie."
                )
            )

    def __processmedia(self, item: dict, func_name: str) -> list:
        self.__logger.info(
            f"Carry out the process of retrieving URLs from each media in the {self.__current_func()} function."
        )

        medias = []

        match func_name:
            case "allmedia":
                images = [
                    index["image_versions2"]["candidates"][0]["url"]
                    for index in item.get(
                        "carousel_media", [item]
                    )
                ]

                videos = [
                    media["video_versions"][0]["url"]
                    for media in item.get(
                        "carousel_media", [item]
                    ) if "video_versions" in media
                ]
                medias.extend(images + videos)

            case "images":
                images = [
                    index["image_versions2"]["candidates"][0]["url"]
                    for index in item.get(
                        "carousel_media", [item]
                    )
                ]
                medias.extend(images)

            case "videos":
                videos = [
                    media["video_versions"][0]["url"]
                    for media in item.get(
                        "carousel_media", [item]
                    ) if "video_versions" in media
                ]
                medias.extend(videos)

        self.__logger.info(
            "The URL of each media has been successfully obtained."
        )
        return medias

    def __download(self, url: str) -> Any:
        self.__logger.info(
            f"Carry out the process to retrieve content, filename, and content_type in the {self.__current_func()} function."
        )

        user_agent = self.__fake.user_agent()
        self.__headers["User-Agent"] = user_agent

        self.__logger.info(
            "Make a request to the URL of the media from which the content will be retrieved using the GET method."
        )

        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=120,
            headers=self.__headers,
        )
        status_code = resp.status_code
        data = resp.content
        if status_code == 200:
            pattern = re.compile(r'\/([^\/?]+\.jpg)')
            matches = pattern.search(url)
            if matches:
                filename = matches.group(1)
            else:
                pattern = re.compile(r'\/([^\/?]+\.mp4)')
                matches = pattern.search(url)
                if matches:
                    filename = matches.group(1)
                else:
                    filename = f"PyGDownloader{datetime.now().strftime('%Y%m%d%H%M%S')}"
            content_type = resp.headers.get("Content-Type")

            self.__logger.info(
                "content, filename, and content type have been successfully obtained."
            )

            return data, filename, content_type
        else:
            self.__logger.error(
                HTTPErrorException(
                    f"Error! status code {resp.status_code} : {resp.reason}"
                )
            )

    def allmedia(self, **kwargs) -> Any:
        self.__logger.info(
            "Retrieves all media from photos and videos from specified Instagram user posts."
        )

        username = kwargs.get("username")
        count = kwargs.get("count", 33)
        max_id = kwargs.get("max_id", None)

        user_agent = self.__fake.user_agent()

        url = f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count}"\
            if max_id else f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count}&max_id={max_id}"

        self.__headers["User-Agent"] = user_agent
        self.__headers["X-Asbd-Id"] = "129477"
        self.__headers["X-Csrftoken"] = self.__Csrftoken()
        self.__headers["X-Ig-App-Id"] = "936619743392459"

        self.__logger.info(
            "Make a request to the URL Instagram User Media using the GET method."
        )

        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=60
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            next_max_id = data.get("next_max_id", "")

            medias = []
            for item in data["items"]:
                medias_result = self.__processmedia(
                    item=item,
                    func_name=self.__current_func()
                )
                medias.extend(medias_result)
            self.__logger.info(
                "The process of retrieving all media and cursor values has been successful."
            )
            return medias, next_max_id
        else:
            self.__logger.error(
                HTTPErrorException(
                    f"Error! status code {resp.status_code} : {resp.reason}"
                )
            )

    def images(self, **kwargs) -> list:
        self.__logger.info(
            "Retrieves images from the specified Instagram user's posts."
        )

        username = kwargs.get("username")
        count = kwargs.get("count", 33)
        max_id = kwargs.get("max_id", None)

        user_agent = self.__fake.user_agent()

        url = f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count}"\
            if max_id else f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count}&max_id={max_id}"

        self.__headers["User-Agent"] = user_agent
        self.__headers["X-Asbd-Id"] = "129477"
        self.__headers["X-Csrftoken"] = self.__Csrftoken()
        self.__headers["X-Ig-App-Id"] = "936619743392459"

        self.__logger.info(
            "Make a request to the URL Images Instagram using the GET method."
        )

        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=60
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            next_max_id = data.get("next_max_id", "")

            medias = []
            for item in data["items"]:
                medias_result = self.__processmedia(
                    item=item,
                    func_name=self.__current_func()
                )
                medias.extend(medias_result)
            self.__logger.info(
                "The process of retrieving images and cursor values has been successful."
            )
            return medias, next_max_id
        else:
            self.__logger.error(
                HTTPErrorException(
                    f"Error! status code {resp.status_code} : {resp.reason}"
                )
            )

    def videos(self, **kwargs) -> list:
        self.__logger.info(
            "Retrieves videos from the specified Instagram user's posts."
        )

        username = kwargs.get("username")
        count = kwargs.get("count", 33)
        max_id = kwargs.get("max_id", None)

        user_agent = self.__fake.user_agent()

        url = f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count}"\
            if max_id else f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count}&max_id={max_id}"

        self.__headers["User-Agent"] = user_agent
        self.__headers["X-Asbd-Id"] = "129477"
        self.__headers["X-Csrftoken"] = self.__Csrftoken()
        self.__headers["X-Ig-App-Id"] = "936619743392459"

        self.__logger.info(
            "Make a request to the URL videos Instagram using the GET method."
        )

        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=60
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            next_max_id = data.get("next_max_id", "")

            medias = []
            for item in data["items"]:
                medias_result = self.__processmedia(
                    item=item,
                    func_name=self.__current_func()
                )
                medias.extend(medias_result)
            self.__logger.info(
                "The process of retrieving videos and cursor values has been successful."
            )
            return medias, next_max_id
        else:
            self.__logger.error(
                HTTPErrorException(
                    f"Error! status code {resp.status_code} : {resp.reason}"
                )
            )

    def linkdownloader(self, link: str):
        self.__logger.info(
            "Retrieve the url from the igdownloader.app API url.")

        link = quote(link)

        user_agent = self.__fake.user_agent()

        url = f"https://v3.igdownloader.app/api/ajaxSearch?recaptchaToken=&q={link}&t=media&lang=id"

        self.__headers["User-Agent"] = user_agent

        self.__logger.info(
            "Make a request to the URL igdownloader.app using the POST method."
        )

        resp = self.__session.request(
            method="POST",
            url=url,
            headers=self.__headers,
            timeout=60
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            html = data.get("data", "")

            div = self.__parser.pyq_parser(
                html,
                'ul[class="download-box"] li div[class="download-items"] div[class="download-items__btn"]'
            )

            medias = []

            for a in div:
                media = self.__parser.pyq_parser(
                    a,
                    'a'
                ).attr("href")
                medias.append(media)

            self.__logger.info(
                "The process of retrieving media has been successful."
            )
            return medias
        else:
            self.__logger.error(
                HTTPErrorException(
                    f"Error! status code {resp.status_code} : {resp.reason}"
                )
            )

    def start_polling(self):
        self.__logger.info("Starting the PyGDTelebot program has gone well.")
        self.__bot.polling(non_stop=False)


if __name__ == "__main__":
    sb = PyGDTelebot()
