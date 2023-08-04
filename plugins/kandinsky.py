from typing import Literal, Self
import asyncio

from dotenv import load_dotenv
import replicate

resolutions = Literal["384", "512", "640", "704", "768", "960", "1024"]


class ImageGenerator:
    def __init__(self: Self) -> None:
        load_dotenv()

    async def generate_image(self: Self, prompt: str = "A moss covered astronaut with a black background", height: int = 512, width: int = 512) -> list[str]:
        num = 1 if height > 640 or width > 640 else 2
        loop = asyncio.get_event_loop()

        try:
            output = await loop.run_in_executor(None, self.actual_image_generator, prompt, height, width, num)

            if isinstance(output, list):
                return output

            return []
        except Exception:
            raise

    def actual_image_generator(self: Self, prompt: str, height: int, width: int, num: int) -> list[str]:
        gen = replicate.run(
            "ai-forever/kandinsky-2.2:ea1addaab376f4dc227f5368bbd8eff901820fd1cc14ed8cad63b29249e9d463",
            input={"prompt": prompt, "height": height, "width": width, "num_inference_steps": 50, "num_outputs": num},
        )
        if isinstance(gen, list):
            return gen
        return []


async def main() -> None:
    from datetime import datetime

    print("starting ", start := datetime.now())
    print(await ImageGenerator().generate_image("photo of landscape with lake and mountains, snowy mountaintops, 4k", 640, 1024))
    print("finished ", fin := datetime.now())
    print("took ", fin - start)


if __name__ == "__main__":
    asyncio.run(main())
