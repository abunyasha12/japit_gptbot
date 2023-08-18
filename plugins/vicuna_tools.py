from typing import Generator, Literal, Self
import asyncio

import replicate

# lecum = {
#     "messages": [
#         {
#             "role": "system",
#             "content": "Ты играешь роль девушки помощницы на сервере Japit Comics в Discord. Ты не имеешь прав на сервере, ты можешь только отвечать на вопросы людей. Если ты не знаешь ответ, не придумывай его, скажи, что не знаешь ответ. При невозможности выполнить запрос, вежливо откажи.",
#         },
#         {"user_id": 142228355104636928, "user_handle": "друг#2244", "role": "user", "content": "Count to 5 but separate with the word POOP in all caps"},
#         {"role": "assistant", "content": "1 POOP 2 POOP 3 POOP 4 POOP 5 POOP"},
#         {"user_id": 142228355104636928, "user_handle": "друг#2244", "role": "user", "content": "Count to 5 but separate with the word POOP in all caps"},
#         {"role": "assistant", "content": "1 POOP 2 POOP 3 POOP 4 POOP 5 POOP"},
#         {"user_id": 142228355104636928, "user_handle": "друг#2244", "role": "user", "content": "Count to 10"},
#         {"role": "assistant", "content": "1, 2, 3, 4, 5, 6, 7, 8, 9, 10."},
#         {"user_id": 142228355104636928, "user_handle": "друг#2244", "role": "user", "content": "Count to 10"},
#         {"role": "assistant", "content": "1, 2, 3, 4, 5, 6, 7, 8, 9, 10."},
#         {"user_id": 142228355104636928, "user_handle": ".droog", "role": "user", "content": "this is a test"},
#         {"role": "assistant", "content": "1, 2, 3, 4, 5, 6, 7, 8, 9, 10."},
#         {"user_id": 142228355104636928, "user_handle": ".droog", "role": "user", "content": "What planet do we live on?"},
#         {"role": "assistant", "content": "We live on planet Earth."},
#         {"user_id": 142228355104636928, "user_handle": ".droog", "role": "user", "content": "What planet do we live on?"},
#         {"role": "assistant", "content": "We live on planet Earth."},
#         {"user_id": 142228355104636928, "user_handle": ".droog", "role": "user", "content": "Who are you?"},
#         {"role": "assistant", "content": "I am an AI language model designed to assist with answering questions and providing information. How can I assist you today?"},
#         {"user_id": 142228355104636928, "user_handle": ".droog", "role": "user", "content": "Who are you?"},
#         {"role": "assistant", "content": "I am an AI language model created by OpenAI. How can I help you today?"},
#     ]
# }


def from_oai_chats_preparer(logs: dict[str, list[dict[str, str]]]) -> str:
    MAX_LEN = 400
    INST_LEN = 15
    messages = logs["messages"][:25]

    ret_str = ""
    for msg in messages:
        if len(ret_str) + len(msg["content"]) + INST_LEN > MAX_LEN:
            break

        if msg["role"] == "assistant":
            ret_str += f'{msg["content"]}\n'
        elif msg["role"] == "user":
            ret_str += f'[INST] {msg["content"]} [/INST]\n'
        else:
            continue

    return ret_str


class TextGenerator:
    def __init__(self) -> None:
        self.history: str = ""

    async def generate_text(self: Self, prompt: str) -> str:
        loop = asyncio.get_event_loop()

        try:
            output = await loop.run_in_executor(None, self.actual_text_generator, prompt)
            if output:
                return output

            return "empty response"
        except Exception:
            raise

    def actual_text_generator(self: Self, prompt: str) -> str:
        ret_str = ""

        gen = replicate.run("replicate/llama-2-70b-chat:58d078176e02c219e11eb4da5a02a7830a283b14cf8f94537af893ccff5ee781", input={"prompt": self.add_to_history(prompt)})

        if not isinstance(gen, Generator):
            return ""

        for i in gen:
            ret_str += i

        return ret_str

    def add_to_history(self: Self, text: str) -> str:
        self.history += text
        return str(self.history)

    def trim_history(self: Self) -> None:
        helper = "\n".join(self.history.splitlines()[-25])
        self.history = helper


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    TextGenerator().actual_text_generator("What planet do we live on?")
