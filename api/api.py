from fastapi import FastAPI
from fastapi.responses import PlainTextResponse, RedirectResponse
from pathlib import Path

app = FastAPI()
sdconfig = Path("sdconfig.csv")


@app.post("/add_lora", tags=["LoRa"])
async def add_lora(lora_filename: str) -> PlainTextResponse:
    with sdconfig.open("a") as f:
        f.write(f'<lora:{lora_filename.replace(".safetensors", "").replace(".pt", "").strip()}:1>\n')

    with sdconfig.open("r") as f:
        return PlainTextResponse(content=f.read())


@app.delete("/del_lora", tags=["LoRa"])
async def del_lora(lora_filename: str) -> PlainTextResponse:
    with sdconfig.open("r") as fin:
        interm = [line for line in fin.readlines() if not line.startswith(lora_filename)]

    with sdconfig.open("w+") as fout:
        for line in interm:
            fout.write(line)

        fout.seek(0)
        return PlainTextResponse(content=fout.read())


@app.get("/get_loras", tags=["LoRa"])
async def get_lora() -> PlainTextResponse:
    """
    Список лор ([`/get_loras`](/get_loras))
    """
    with sdconfig.open("r") as f:
        return PlainTextResponse(content=f.read())


@app.head("/", tags=["Index"], response_model=None)
@app.get("/", tags=["Index"], response_model=None, response_class=RedirectResponse, responses={200: {"description": "HTML Response"}, 307: {"description": "Redirect Response"}})
async def index() -> RedirectResponse:
    """
    Документация ([`/docs`](/docs))
    """

    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=7859)
