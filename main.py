import os
import json
from PIL import Image
import requests
import numpy as np
import cv2
import base64


from apify_client import ApifyClient
token = os.getenv('APIFY_TOKEN')
apify_client = ApifyClient(token)

kv_store_id = os.getenv('APIFY_DEFAULT_KEY_VALUE_STORE_ID')
input = apify_client.key_value_store(kv_store_id).get_record('INPUT')["value"]  
 

""" input = {
  "input_type": "url",
  "input_image": "https://images4.programmersought.com/934/e8/e89758ae0ed991f1c8aba947addec9e6.png",
  "lang": "en",
  "ocr": "paddle", # or tesseract
  "output_format": "bbox" # bbox,txt or pdf
} """

def download_image(img):
    if img.startswith("http"):
        res = requests.get(img, stream=True)
        block_size=1024
        with open("tmp.jpg", "wb") as file:
            for data in res.iter_content(block_size):
                file.write(data)
        img = "tmp.jpg"

    with open(img, "rb") as file:
        np_arr = np.frombuffer(file.read(), dtype=np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return image


if input["input_type"] == "url":
    np_image = download_image(input["input_image"])
    print(np_image.shape)

elif input["input_type"] is "base64":
    b64data = input["input_image"]
    raw_image = base64.b64decode(b64data)
    np_arr = np.frombuffer(raw_image, dtype=np.uint8)
    np_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    print(np_image.shape)
    
else:
    output = {"error": "Wrong input type", "response":None}
    #apify_client.key_value_store(kv_store_id).set_record('OUTPUT', output, content_type="application/json")



if input["ocr"] == "paddle":
# You have the input now, do stuff with it
    from paddleocr import PaddleOCR
    from pylatex import Document, MiniPage, TextBlock, MediumText, HugeText, \
    SmallText, VerticalSpace, HorizontalSpace
    from pylatex.utils import bold
    import pylatex.config as cf

    ocr = PaddleOCR(use_angle_cls=False, lang=input["lang"], use_gpu=False) # need to run only once to download and load model into memory

    result = ocr.ocr(np_image, cls=False)

    if input["output_format"] is "bbox":
        output = {}
        i=0
        for line in result:
            output[i] = {"bbox": line[0], "text":line[1][0]}
            i=i+1
            print(line)

        output = {"response": output, "error":None}

    elif input["output_format"] is "pdf":
    #pixel_to_inch = 1/72
        img_width = np_image.shape[1] / 72
        img_height = np_image.shape[0] / 72
        print(img_height, img_width)

        cf.active = cf.Version1(indent=False)
        geometry_options = {"margin": "0in", "paperwidth": "{}in".format(img_width), "paperheight": "{}in".format(img_height)}
        pdf_export = Document(indent=False, geometry_options=geometry_options)
        pdf_export.change_length("\TPHorizModule", "1in")
        pdf_export.change_length("\TPVertModule", "1in")
        with pdf_export.create(MiniPage(width=r"\textwidth")) as page:
            for line in result:
                with page.create(TextBlock((line[0][1][0]-line[0][0][0])/72,line[0][0][0] / 72, line[0][0][1] / 72)):
                    page.append(line[1][0])

        pdf_export.generate_pdf("pdf_export", clean_tex=False)
        #os.rename("./pdf_export.tex", "./tex_export.tex")


        output = None
        with open("pdf_export.pdf", "rb") as file:
            output = base64.b64encode(file.read())

        output = {"response": output.decode('utf-8'), "error":None}
        

    elif input["output_format"] is "txt":
        output = {"error": "Paddle OCR does not support txt output", "response":None}
    
    else:
        output = {"error": "Unsupported output format", "response":None}
        #apify_client.key_value_store(kv_store_id).set_record('OUTPUT', output, content_type="application/json")


elif input["ocr"] == "tesseract":
    import subprocess

    cv2.imwrite("./tmp.jpg", np_image)

    if input["output_format"] is "txt":
        subprocess.run(["tesseract","./tmp.jpg", "output", "-l", "{}".format(input["lang"])])
        output_txt = None
        with open("output.txt", "r") as file:
            output_txt = file.read()
        output = {"response": output_txt, "error":None}

    elif input["output_format"] is "pdf":
        subprocess.run(["tesseract", "./tmp.jpg", "output", "-l", "{}".format(input["lang"]), "pdf"])
        output = None
        with open("output.pdf", "rb") as file:
            output = base64.b64encode(file.read())

        output = {"response": output.decode('utf-8'), "error":None}
    
    elif input["output_format"] is "json":
        output = {"error": "Tesseract OCR does not support bbox output", "response":None}
    
    else:
        output = {"error": "Unsupported output format", "response":None}


else:
    output = {"error": "Unsupported OCR", "response":None}

print(output)
output = json.dumps(output)

apify_client.key_value_store(kv_store_id).set_record('OUTPUT', output, content_type="application/json")

datasets = apify_client.datasets().list()
if len(datasets.items) == 0:
    apify_client.datasets().get_or_create().push_items(output)
apify_client.dataset(datasets.items[0]).push_items(output) 
