import io
import os
import re
import json
import logging
import inspect
import hashlib

from requests.sessions import Session
from telebot import types, async_telebot
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
        self.__bot = async_telebot.AsyncTeleBot(token=TOKEN)

        self.__cookie = os.environ.get("IG_COOKIE")

        self.__parser = HtmlParser()
        self.__session = Session()
        self.__fake = Faker()

        self.__headers = dict()
        self.__headers["Accept"] = "application/json, text/plain, */*"
        self.__headers["Accept-Language"] = "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
        self.__headers["Sec-Fetch-Dest"] = "empty"
        self.__headers["Sec-Fetch-Mode"] = "cors"
        self.__headers["Sec-Fetch-Site"] = "same-site"
        self.__headers["Cookie"] = self.__cookie

        self.__http_error_status_code = None
        self.__http_error_reason = None
        self.__func_name = None
        self.__is_stop = False
        self.__medias = []
        self.__next_max_id = None
        self.__msg_text = ""
        self.__pathdir = os.getcwd()

        if "log" not in os.listdir(self.__pathdir): self.__mkdir(folder_name="log")

        setup_logging()
        self.__logger = logging.getLogger(self.__class__.__name__)

        self.__current_func = lambda: inspect.getouterframes(inspect.currentframe())[1][3]
        self.__delws = lambda text: re.sub(r'\s', '', text)
        self.__mkdir = lambda folder_name: os.mkdir(path=os.path.join(self.__pathdir, folder_name))
        self.__instructions = lambda chat_id: self.__bot.send_message(chat_id=chat_id, text=f"Unrecognized command. Say what?")
        

        @self.__bot.message_handler(commands=["help"])
        async def helper(message):
            id = message.chat.id
            
            await self.__bot.send_message(
                chat_id=id,
                text=(
                    "I can help you using this <b>PyGDTelebot</b>.\n"
                    "You can control me by sending these commands :\n\n"
                    "/start - Starting the <a href='https://t.me/itsPyGD_bot'>bot</a>\n"
                    "/features - Shows the features of this bot.\n"
                    "/stop - Stops media delivery.\n\n"
                    "📖 Description of features:\n"
                    "   ✮ <i>All Media</i> - Images and Videos from Instagram user posts.\n"
                    "   ✮ <i>Images</i> - Images from Instagram user posts.\n"
                    "   ✮ <i>Videos</i> - Videos from Instagram user posts.\n"
                    "   ✮ <i>Link Downloader</i> - Media form the given URL.\n\n"
                    "😱 Implementation of each feature :\n"
                    "   ✮ <i>All Media, Images, Videos</i> :\n"
                    "       ○ Complete this :\n"
                    "           username = <b>(Required)</b>\n"
                    "           max_id = <b>(Optional)</b>\n"
                    "       ○ Application example :\n"
                    "           username = iam_muhfalihr\n"
                    "         -------------------- or --------------------\n"
                    "           username = iam_muhfalihr\n"
                    "           max_id = 12345678_987654321\n\n"
                    "   ✮ <i>Link Downloader</i> :\n"
                    "       Send Instagram User Post link!\n\n"
                    "Please use this bot happily and calmly.\n"
                    "Greetings of peace from @muhammadfalihromadhoni 💙\n\n"
                    "🌟 Follow my Github <a href='https://github.com/muhfalihr'>muhfalihr</a>\n"
                    "🚀 Follow my Instagram <a href='https://www.instagram.com/_____mfr.py/'>@_____mfr.py</a>"
                ),
                parse_mode='HTML'
            )

        @self.__bot.message_handler(commands=["features"])
        async def inlinekeybutton(message):
            markup = types.InlineKeyboardMarkup()
            allmedia = types.InlineKeyboardButton("All Media", callback_data='All Media')
            images = types.InlineKeyboardButton("Images", callback_data='Images')
            videos = types.InlineKeyboardButton("Videos", callback_data='Videos')
            linkdownloader = types.InlineKeyboardButton("Link Downloader", callback_data="Link Downloader")

            markup.add(allmedia, images, videos, linkdownloader)

            await self.__bot.send_message(message.chat.id, "🧐 Select one of the downloader features:", reply_markup=markup)

        @self.__bot.callback_query_handler(func=lambda call: True)
        async def option(call):
            id = call.message.chat.id
            call_data = call.data

            match call_data:
                case "All Media" | "Images" | "Videos":
                    self.__func_name = call_data

                    message = await self.__bot.send_message(
                        chat_id=id,
                        text=(
                            f"<i><b>{call_data} Feature</b></i>\n\n"
                            "<code>username = (Required)</code>\n"
                            "<code>max_id = (Optional)</code>\n"
                        ),
                        parse_mode="HTML"
                    )
                    await self.__bot.reply_to(
                        message=message,
                        text=(
                            "OK. Complete this!.\n"
                            "Confused? See /help."
                        )
                    )

                case "Link Downloader":
                    self.__func_name = call_data

                    await self.__bot.send_message(
                        chat_id=id,
                        text=(
                            "OK. Send Instagram User Post link!.\n"
                            "Confused? See /help."
                        )
                    )

        @self.__bot.message_handler(commands=["start", "hello"])
        async def introduction(message):
            id = message.chat.id
            username = message.from_user.username

            await self.__bot.reply_to(message=message, text=f"Welcome👋, {username}")
            await self.__bot.send_message(
                chat_id=id,
                text="If you are still confused when using this <a href='https://t.me/itsPyGD_bot'>bot</a>, see /help.",
                parse_mode="HTML"
            )

        @self.__bot.message_handler(commands=["report"])
        async def report(message):
            await self.__bot.send_message(
                chat_id=message.chat.id,
                text=(
                    "Report a Problem 🙏 : ...\n\n"
                    "Copy and complete the report text above."
                )
            )

        @self.__bot.message_handler(func=lambda message: True if "Report a Problem 🙏" in message.text else False)
        async def savereport(message):
            id = message.chat.id
            user = message.from_user.username

            if "report" not in os.listdir(self.__pathdir): self.__mkdir(folder_name="report")

            with open(f"report/report-{user}-{datetime.now().strftime('%Y%m%d%H%M%S')}.txt", "w") as report_file:
                report_file.write(message.text)

            await self.__bot.send_message(chat_id=id,text="Report sent successfully. Thank you🙏. /help")

        @self.__bot.message_handler(commands=["stop"])
        async def stop_generate(message):
            self.__is_stop = True

        @self.__bot.message_handler(func=lambda message: True if message.text.upper() in ["Y", "N"] else False)
        async def is_continue(message):
            id = message.chat.id
            match message.text.upper():
                case "Y":
                    self.__is_stop = False
                    await self.__bot.send_message(chat_id=id, text="🟢 Continue sending media...")
                    await self.__media_processor(id=id)

                case "N":
                    self.__is_stop = False
                    await self.__bot.send_message(chat_id=id, text="OK, if you don't want to continue. /features")
                
                case _:
                    await self.__instructions(chat_id=id)

        @self.__bot.message_handler(func=lambda message: True if self.__func_name in ["All Media", "Images", "Videos"] and "=" in message.text else False)
        async def media_sender(message):
            id = message.chat.id
            msg = message.text

            parameters = dict()
            parameters.update({"feature": self.__func_name})

            for param in msg.split("\n"):
                parameter = self.__delws(param).split("=")
                parameters.update({parameter[0]: parameter[1]})

            if parameters:
                await self.__bot.send_message(
                    chat_id=id,
                    text=(
                        "Please Wait....\n"
                        f"🟢 This process may take a {'little' if self.__func_name != 'Videos' else 'long'} time so please be patient and wait until the notification message appears."
                    )
                )

                try:
                    medias, next_max_id = self.__media_url_getter(**parameters)

                    self.__medias = medias
                    self.__next_max_id = next_max_id
                    self.__msg_text = msg

                    await self.__media_processor(id=id)

                except Exception:
                    await self.__http_error(chat_id=id)

            else:
                await self.__instructions(chat_id=id)

        @self.__bot.message_handler(func=lambda message: True if self.__func_name == "Link Downloader" and message else False)
        async def media_sender_from_ld(message):
            id = message.chat.id
            param = message.text

            pattern = r'https:\/\/www\.instagram\.com\/.+\/.+\/\?(utm_source=ig_web_copy_link|igsh=.+)'

            try:
                if re.match(pattern=pattern, string=param):
                    await self.__bot.send_message(
                        chat_id=id,
                        text="🟢 Please Wait...."
                    )

                    try:
                        medias = self.__linkdownloader(param)

                        media_group = []

                        for media in medias:
                            data, filename, content_type = self.__download(media)

                            databyte = io.BytesIO(data)
                            databyte.name = filename

                            if databyte:
                                if len(media_group) == 5: media_group.clear()

                                if len(media_group) < 5:
                                    if "image" in content_type:
                                        media_group.append(types.InputMediaPhoto(media=databyte))
                                    elif "video" in content_type:
                                        media_group.append(types.InputMediaVideo(media=databyte))

                                if len(media_group) == 5:
                                    await self.__bot.send_media_group(chat_id=id,media=media_group)

                        if media_group:
                            await self.__bot.send_media_group(chat_id=id,media=media_group)

                        await self.__bot.send_message(chat_id=id, text="Done 😊")

                    except Exception:
                        await self.__http_error(chat_id=id)

                else:
                    await self.__instructions(chat_id=id)

            except IndexError:
                await self.__instructions(chat_id=id)
    
    async def __http_error(self, chat_id: str):
        if self.__http_error_reason and self.__http_error_status_code is not None:
            await self.__bot.send_message(
                chat_id=chat_id,
                text=f"❌ Error! status code {self.__http_error_status_code} : {self.__http_error_reason}"
            )
            await self.__bot.send_message(chat_id=chat_id, text="Sorry🙏 Please report this issue. /report")
        else:
            await self.__bot.send_message(chat_id=chat_id, text=f"❌ Error! A request to the Telegram API was unsuccessful.")
            await self.__bot.send_message(chat_id=chat_id, text="Sorry🙏 Please Try Again 😥. /report")

    async def __media_processor(self, id: str):
        
        medias_copy = list(self.__medias)

        media_group = []
        for media in medias_copy:

            if self.__is_stop: break

            data, filename, content_type = self.__download(media)
            self.__medias.pop(0)

            databyte = io.BytesIO(data)
            databyte.name = filename

            match self.__func_name:
                case "All Media" | "Videos":
                    if len(media_group) == 3: media_group.clear()

                    if len(media_group) < 3:
                        if "image" in content_type:
                            media_group.append(types.InputMediaPhoto(media=databyte))
                        if "video" in content_type:
                            media_group.append(types.InputMediaVideo(media=databyte))
                    
                    try:
                        if len(media_group) == 3:
                            await self.__bot.send_media_group(id=id,media=media_group)
                    except Exception:
                        await self.__bot.send_message(chat_id=id, text="😥 Failed to send media.")

                case "Images":
                    if len(media_group) == 5: media_group.clear()

                    if len(media_group) < 5:
                        media_group.append(types.InputMediaPhoto(media=databyte))
                    
                    try:
                        if len(media_group) == 5:
                            await self.__bot.send_media_group(chat_id=id, media=media_group)
                    except Exception:
                        await self.__bot.send_message(chat_id=id, text="😥 Failed to send media.")
        try:
            if media_group: await self.__bot.send_media_group(chat_id=id,media=media_group)
        except Exception: pass

        if self.__is_stop:
            await self.__bot.send_message(chat_id=id, text=f"🛑 Stops media delivery...")
            self.__func_name = self.__func_name
            await self.__bot.send_message(chat_id=id, text="Do you want to continue? (Y/N)")
            self.__medias = self.__medias
        else:
            if self.__next_max_id:
                await self.__bot.send_message(
                    chat_id=id,
                    text=(
                        f"Your previous message : \n<code>{self.__msg_text}</code>\n\n"
                        f"Max ID for next media = <code>{self.__next_max_id}</code>"
                    ),
                    parse_mode="HTML"
                )
            else:
                await self.__bot.send_message(chat_id=id, text="Done 😊")

            await self.__bot.send_message(chat_id=id,text="To continue or not, specify in /features.")
                

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

    def __download(self, url: str) -> Any:
        self.__logger.info(f"Carry out the process to retrieve content, filename, and content_type in the {self.__current_func()} function.")

        user_agent = self.__fake.user_agent()
        self.__headers["User-Agent"] = user_agent

        self.__logger.info("Make a request to the URL of the media from which the content will be retrieved using the GET method.")

        resp = self.__session.request(
            method="GET",
            url=url,
            timeout=240,
            headers=self.__headers
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

            self.__logger.info("content, filename, and content type have been successfully obtained.")

            return data, filename, content_type
        else:
            self.__http_error_status_code = resp.status_code
            self.__http_error_reason = resp.reason

            self.__logger.error(
                HTTPErrorException(
                    f"Error! status code {resp.status_code} : {resp.reason}"
                )
            )

    def __media_url_getter(self, **kwargs) -> (list, str):

        feature = kwargs.get("feature")

        self.__logger.info(f"Retrieves {feature} from specified Instagram user posts.")

        username = kwargs.get("username")
        count = kwargs.get("count", 33)
        max_id = kwargs.get("max_id", None)

        user_agent = self.__fake.user_agent()

        url = f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count}&max_id={max_id}"\
            if max_id else f"https://www.instagram.com/api/v1/feed/user/{username}/username/?count={count}"

        self.__headers["User-Agent"] = user_agent
        self.__headers["X-Asbd-Id"] = "129477"
        self.__headers["X-Csrftoken"] = self.__Csrftoken()
        self.__headers["X-Ig-App-Id"] = "936619743392459"

        self.__logger.info("Make a request to the URL Instagram User Media using the GET method.")

        resp = self.__session.request(
            method="GET",
            url=url,
            headers=self.__headers,
            timeout=240
        )
        status_code = resp.status_code
        content = resp.content
        if status_code == 200:
            response = content.decode('utf-8')
            data = json.loads(response)
            next_max_id = data.get("next_max_id", None)

            medias = []

            for item in data.get("items", []):
                match feature:
                    case "All Media":
                        if item.get("carousel_media"):
                            images = [
                                max(i.get("image_versions2", {}).get("candidates", []), key=lambda x: x.get("width", 0) * x.get("height", 0)).get("url")
                                for i in item.get("carousel_media", [])
                                if i.get("video_versions", None) == None
                            ]
                            medias.extend(images)

                        elif item.get("video_versions", None) == None:
                            images = [max(item.get("image_versions2", {}).get("candidates", []), key=lambda x: x.get("width", 0) * x.get("height", 0)).get("url")]
                            medias.extend(images)

                        videos = [
                                max(i.get("video_versions", []), key=lambda x: x.get("width", 0) * x.get("height", 0)).get("url")
                                for i in item.get("carousel_media", [item])
                                if i.get("video_versions")
                            ]
                        medias.extend(videos)

                    case "Images":
                        if item.get("carousel_media"):
                            images = [
                                max(i.get("image_versions2", {}).get("candidates", []), key=lambda x: x.get("width", 0) * x.get("height", 0)).get("url")
                                for i in item.get("carousel_media", [])
                                if i.get("video_versions", None) == None
                            ]
                            medias.extend(images)

                        elif item.get("video_versions", None) == None:
                            images = [max(item.get("image_versions2", {}).get("candidates", []), key=lambda x: x.get("width", 0) * x.get("height", 0)).get("url")]
                            medias.extend(images)

                    case "Videos":
                        videos = [
                            max(i.get("video_versions", []), key=lambda x: x.get("width", 0) * x.get("height", 0)).get("url")
                            for i in item.get("carousel_media", [item])
                            if i.get("video_versions")
                        ]
                        medias.extend(videos)
            
            return medias, next_max_id
                    
        else:
            self.__http_error_status_code = resp.status_code
            self.__http_error_reason = resp.reason

            self.__logger.error(
                HTTPErrorException(
                    f"Error! status code {resp.status_code} : {resp.reason}"
                )
            )

    def __linkdownloader(self, link: str):
        self.__logger.info("Retrieve the url from the igdownloader.app API url.")

        link = quote(link)

        user_agent = self.__fake.user_agent()

        url = f"https://v3.igdownloader.app/api/ajaxSearch?recaptchaToken=&q={link}&t=media&lang=id"

        self.__headers["User-Agent"] = user_agent

        self.__logger.info("Make a request to the URL igdownloader.app using the POST method.")

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

            for a in div:
                media = self.__parser.pyq_parser(a, 'a').attr("href")
                yield media

            self.__logger.info("The process of retrieving media has been successful.")
        else:
            self.__http_error_status_code = resp.status_code
            self.__http_error_reason = resp.reason

            self.__logger.error(
                HTTPErrorException(
                    f"Error! status code {resp.status_code} : {resp.reason}"
                )
            )

    async def start_polling(self):
        self.__logger.info("Starting the PyGDTelebot program has gone well.")
        await self.__bot.polling(non_stop=False, timeout=240)


if __name__ == "__main__":
    sb = PyGDTelebot()
