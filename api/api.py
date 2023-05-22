from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse, RedirectResponse
from pathlib import Path
from SD_tools import file_ops
from typing import Annotated

app = FastAPI()
sdconfig = Path("sdconfig.csv")
fops = file_ops()


@app.get("/get_loras", tags=["LoRa"], summary="Получить список лор")
async def get_lora() -> PlainTextResponse:
    """
    Вовзращает список лор в `PlainTextResponse`
    """
    return PlainTextResponse(await fops.get_lora())


@app.post("/add_lora", tags=["LoRa"], summary="Добавить лору")
async def add_lora(lora_filename: Annotated[str, Query(description="Название файла с расширением либо без", min_length=1)]) -> PlainTextResponse:
    """
    Добавляет лору, возвращает обновленный список лор в `PlainTextResponse`
    """
    return PlainTextResponse(await fops.add_lora(lora_filename))


@app.delete("/del_lora", tags=["LoRa"], summary="Удалить лору")
async def del_lora(lora_filename: Annotated[str, Query(description="Название лоры для удаления, полное или частичное", min_length=1)]) -> PlainTextResponse:
    """
    Удаляет лору по названию, возвращает обновленный список лор в `PlainTextResponse`.
    """
    return PlainTextResponse(await fops.del_lora(lora_filename))


@app.head("/", tags=["Index"], response_model=None, include_in_schema=False)
@app.get(
    "/",
    tags=["Index"],
    response_model=None,
    response_class=RedirectResponse,
    responses={200: {"description": "HTML Response"}, 307: {"description": "Redirect Response"}},
    include_in_schema=False,
)
async def index() -> RedirectResponse:
    """
    Документация ([`/docs`](/docs))
    """

    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=7859)
