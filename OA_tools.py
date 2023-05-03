from revChatGPT.V3 import Chatbot
import openai
import openai.error as oe
from typing import Literal


resolutions = Literal["256", "512"]


class InvalidRequest(Exception):
    pass


class ChatGPT():

    def __init__(self, oaitoken) -> None:
        self.oaitoken = oaitoken
        self.user = Chatbot(api_key=oaitoken,
                            system_prompt='''
        Ты играешь роль девушки помощницы на сервере Japit Comics в Discord.
        Ты не имеешь прав на сервере, ты можешь только отвечать на вопросы людей.
        Если ты не знаешь ответ, не придумывай его, скажи, что не знаешь ответ.
        При невозможности выполнить запрос, вежливо откажи.''')

    async def chat_completion(self, prompt: str, convo_id=1093166962428882996) -> str:
        cvid = str(convo_id)
        user = self.user
        if user is None:
            text = "*Bot is not initialised!*"
            return text
        try:
            text = await user.ask_async(prompt, role="user", convo_id=cvid)
            return text
        except Exception as e:
            print(e.__class__.__name__, e)
            text = "exception"
            return text[:2000]

    async def generate_image(self, prompt: str, resolution) -> str:
        if self.oaitoken is None:
            raise Exception
        try:
            image_url = await openai.Image.acreate(
                api_key=self.oaitoken,
                prompt=prompt,
                n=1,
                size=f"{resolution}x{resolution}"
            )
            return image_url["data"][0]["url"]  # type:ignore
        except oe.InvalidRequestError:
            print("InvalidRequestError Your request was rejected as a result of our safety system. Your prompt may contain text that is not allowed by our safety system.")
            raise InvalidRequest
        except Exception as e:
            print(e.__class__.__name__, e)
            text = "exception"
            return text
