import gradio as gr
import SD_tools as SD

fops = SD.file_ops()


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
            add_lora_text = gr.Textbox(placeholder="hutao.safetensors", label="LoRa filename to add")
            add_lora = gr.Button(value="Add LoRa")
            del_lora_text = gr.Textbox(placeholder="hutao.safetensors", label="LoRa filename to delete")
            del_lora = gr.Button(value="Delete LoRa")
            add_lora.click(fn=fops.add_lora, inputs=add_lora_text, outputs=output_box)
            del_lora.click(fn=fops.del_lora, inputs=del_lora_text, outputs=output_box)

demo.launch()
