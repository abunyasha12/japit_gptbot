from typing import Literal, Self
import asyncio

from dotenv import load_dotenv
import replicate

resolutions = Literal["384", "512", "640", "704", "768", "960", "1024"]


class ImageGenerator:
    def __init__(self: Self) -> None:
        load_dotenv()

    async def generate_image(self: Self, prompt: str = "A moss covered astronaut with a black background", height: int = 512, width: int = 512) -> list:
        num = 1 if height > 640 or width > 640 else 2
        loop = asyncio.get_event_loop()

        try:
            print("TRYING")
            output = await loop.run_in_executor(None, self.actual_image_generator, prompt, height, width, num)
            print("GOT IMAGES")

            if isinstance(output, list):
                return output

            return []
        except Exception:
            raise

    def actual_image_generator(self: Self, prompt: str, height: int, width: int, num: int):
        return replicate.run(
            "ai-forever/kandinsky-2.2:ea1addaab376f4dc227f5368bbd8eff901820fd1cc14ed8cad63b29249e9d463",
            input={"prompt": prompt, "height": height, "width": width, "num_inference_steps": 50, "num_outputs": num},
        )


async def main() -> None:
    await ImageGenerator().generate_image()


if __name__ == "__main__":
    asyncio.run(main())
