from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse, RedirectResponse
from pathlib import Path
import SD_tools as SD
from typing import Annotated
import gradio as gr

app = FastAPI()
sdconfig = Path("sdconfig.csv")
fops = SD.file_ops()


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


def simple() -> str:
    SD.refresh_loras()
    return SD.RAW_LORALIST


with gr.Blocks() as demo:
    gr.Markdown(value="NIGGAS")
    with gr.Row():
        with gr.Column():
            output_box = gr.Textbox(value=SD.RAW_LORALIST, label="List of loras")
            rld_btn = gr.Button(value="Reload lora list")
            rld_btn.click(fn=simple, outputs=output_box)
        with gr.Column():
            gr_add_lora_text = gr.Textbox(placeholder="hutao.safetensors", label="LoRa filename to add")
            gr_add_lora = gr.Button(value="Add LoRa")
            gr_del_lora_text = gr.Textbox(placeholder="hutao.safetensors", label="LoRa filename to delete")
            gr_del_lora = gr.Button(value="Delete LoRa")
            gr_add_lora.click(fn=fops.add_lora, inputs=gr_add_lora_text, outputs=output_box)
            gr_del_lora.click(fn=fops.del_lora, inputs=gr_del_lora_text, outputs=output_box)


app = gr.mount_gradio_app(app, demo, path="/gradio")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=7859)
