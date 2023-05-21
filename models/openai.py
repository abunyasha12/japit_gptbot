import openai
from typing import TypedDict
from dataclasses import dataclass
from pydantic import BaseModel, Field


class ConversationLog(BaseModel):
    """Основная единица лога"""

    user_id: int | None = Field(default=None, title="", description="")
    user_handle: str | None = None
    role: str = "assistant"
    content: str = Field(...)


class Conversation(BaseModel):
    """Модель со всеми логами"""

    messages: list[ConversationLog] = Field(..., min_items=1)


class ChatGPTResponse_message_message(TypedDict):
    """Класс сообщения"""

    role: str
    content: str


@dataclass
class ChatGPTResponse_message:
    """Промежуточный класс сообщений"""

    index: int
    message: ChatGPTResponse_message_message
    finish_reason: str


@dataclass
class ChatGPTResponse_usage:
    """Класс со статистикой запроса"""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ChatGPTResponse:
    """
    Класс ответа от ЧатЖПТ со всеми параметрами

    Example

    {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677652288,
    "choices": [{
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "\n\nHello there, how may I assist you today?",
        },
        "finish_reason": "stop"
    }],
    "usage": {
        "prompt_tokens": 9,
        "completion_tokens": 12,
        "total_tokens": 21
    }
    }
    """

    id: str
    object: str
    created: int
    choices: list[ChatGPTResponse_message]
    usage: ChatGPTResponse_usage


class OpenAI_Typed:
    """типизированный Класс ОпенАИ"""

    api_key: str | None = openai.api_key

    class ChatCompletion(openai.ChatCompletion):
        def __init__(self, engine: str | None = None, **kwargs):
            super().__init__(engine, **kwargs)

        @classmethod
        async def acreate(cls, *args, **kwargs) -> str:
            raw_response: ChatGPTResponse = await super().acreate(*args, **kwargs)  # type: ignore[override]

            return (
                raw_response.choices[0].message["content"]
                if hasattr(raw_response, "choices") and raw_response.choices[0] and raw_response.choices[0].message and "content" in raw_response.choices[0].message
                else ""
            )
