from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pathlib import Path

app = FastAPI()
sdconfig = Path("sdconfig.csv")


@app.post("/add_lora")
async def add_lora(lora_filename: str) -> PlainTextResponse:
    with sdconfig.open("a") as f:
        f.write(f'<lora:{lora_filename.replace(".safetensors", "").replace(".pt", "").strip()}:1>\n')

    with sdconfig.open("r") as f:
        return PlainTextResponse(content=f.read())


@app.post("/del_lora")
async def del_lora(lora_filename: str) -> PlainTextResponse:
    with sdconfig.open("r") as fin:
        interm = [line for line in fin.readlines() if not line.startswith(lora_filename)]

    with sdconfig.open("w+") as fout:
        for line in interm:
            fout.write(line)

        fout.seek(0)
        return PlainTextResponse(content=fout.read())


@app.get("/get_loras")
async def get_lora() -> PlainTextResponse:
    with sdconfig.open("r") as f:
        return PlainTextResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=7859)
