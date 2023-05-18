# from revChatGPT.V3 import Chatbot
import openai
import openai.error as oe
from typing import Literal
import os, os.path
import json


resolutions = Literal["256", "512"]


class InvalidRequest(Exception):
    pass


SYSTEM_PROMPT = """Ты играешь роль девушки помощницы на сервере Japit Comics в Discord. Ты не имеешь прав на сервере, ты можешь только отвечать на вопросы людей. Если ты не знаешь ответ, не придумывай его, скажи, что не знаешь ответ. При невозможности выполнить запрос, вежливо откажи."""


class ChatGPT:
    def __init__(self, oaitoken) -> None:
        self.oaitoken = oaitoken
        self.conversations = {}
        for item in os.listdir("./chats/"):
            with open(f"./chats/{item}", encoding="utf-8") as file:
                self.conversations.update({item.replace(".json", ""): json.load(file)})

    def add_to_conversation(self, convo_id: str, author: str, text: str) -> None:
        text_dict = {"role": author, "content": text}

        if not os.path.isfile(path=f"./chats/{convo_id}.json"):  # проверяет json с историей сообщений для конкретного канала. если его нет, создает и грузит в память
            with open(f"./chats/{convo_id}.json", "w", encoding="utf-8") as file:
                json.dump(obj={"messages": [{"role": "system", "content": SYSTEM_PROMPT}]}, fp=file, indent=4, ensure_ascii=False)
            with open(f"./chats/{convo_id}.json", "r", encoding="utf-8") as file:
                self.conversations.update({convo_id: json.load(file)})

        self.conversations[convo_id]["messages"].append(text_dict)
        with open(f"./chats/{convo_id}.json", "w", encoding="utf-8") as file:
            json.dump(self.conversations[convo_id], file, indent=4, ensure_ascii=False)

    async def chat_completion(self, prompt: str, convo_id="1093166962428882996") -> str:
        openai.api_key = self.oaitoken
        self.add_to_conversation(convo_id, "user", prompt)
        messages = self.conversations[convo_id]["messages"][-15:]
        try:
            text = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=messages)
            self.add_to_conversation(convo_id, "assistant", text.choices[0].message["content"])  # type: ignore
            return str(text.choices[0].message["content"])[:1800]  # type: ignore
        except Exception as e:
            return f"{e.__class__.__name__} {e}"

    async def generate_image(self, prompt: str, resolution) -> str:
        if self.oaitoken is None:
            raise Exception

        try:
            image_url = await openai.Image.acreate(
                api_key=self.oaitoken,
                prompt=prompt,
                n=1,
                size=f"{resolution}x{resolution}",
            )
            return image_url["data"][0]["url"]  # type:ignore
        except oe.InvalidRequestError:
            print("InvalidRequestError: Your request was rejected as a result of our safety system. Your prompt may contain text that is not allowed by our safety system.")
            raise InvalidRequest
        except Exception as e:
            print(e.__class__.__name__, e)
            text = "exception"
            return text
