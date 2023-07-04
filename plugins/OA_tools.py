# from revChatGPT.V3 import Chatbot
import json
from pathlib import Path
from typing import Literal

import openai
import openai.error as oe

from plugins.openai import Conversation, ConversationLog, OpenAI_Typed

resolutions = Literal["256", "512"]


class InvalidRequest(Exception):
    pass


SYSTEM_PROMPT = """Ты играешь роль девушки помощницы на сервере Japit Comics в Discord. Ты не имеешь прав на сервере, ты можешь только отвечать на вопросы людей. Если ты не знаешь ответ, не придумывай его, скажи, что не знаешь ответ. При невозможности выполнить запрос, вежливо откажи."""  # noqa: E501


class ChatGPT:
    def __init__(self, oaitoken: str) -> None:
        self.oaitoken = oaitoken
        self.conversations: dict[int, Conversation] = {}

        for item in (Path(".") / "chats").iterdir():
            with item.open(encoding="utf-8") as file:
                self.conversations.update({int(item.stem): Conversation(**json.load(file))})

    def add_to_conversation(self, conversation: ConversationLog, convo_id: int = 1093166962428882996) -> None:
        path = Path(".") / "chats" / f"{convo_id}.json"

        if not path.is_file() or not self.conversations[convo_id]:  # проверяет json с историей сообщений для конкретного канала. если его нет, создает и грузит в память
            self.conversations[convo_id] = Conversation(messages=[ConversationLog(role="system", content=SYSTEM_PROMPT), conversation])

        else:
            self.conversations[convo_id].messages.append(conversation)

        with path.open("w", encoding="utf-8") as file:
            json.dump(self.conversations[convo_id].dict(exclude_none=True), file, indent=4, ensure_ascii=False)

    async def chat_completion(self, conversation: ConversationLog, convo_id: int = 1093166962428882996) -> str:
        openai.api_key = self.oaitoken
        self.add_to_conversation(conversation, convo_id)
        messages = [m.dict(include={"role", "content"}) for m in self.conversations[convo_id].messages[-10:]]

        try:
            content: str = await OpenAI_Typed.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=messages)

            self.add_to_conversation(ConversationLog(content=content), convo_id)

            return content
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
