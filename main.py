### First get input
from apify_client import ApifyClient
import os
import json

# Unfortunately, the env vars are only available on the Apify platform
# For local runs you will have to comment out the client and mock the values
#token = os.getenv('API_TOKEN')
#apify_client = ApifyClient(token)

# On Apify platform, input is saved in local Key-Value Store as INPUT record
kv_store_id = os.getenv('APIFY_DEFAULT_KEY_VALUE_STORE_ID')
input = apify_client.key_value_store(kv_store_id).get_record('INPUT')['INPUT']
 
""" input = {
  "image_url": "https://aescripts.com/media/catalog/product/cache/1/image/9df78eab33525d08d6e5fb8d27136e95/2/d/2df_simple-text_info_quick-start.png",
  "lang": "en"
}  """
print(input)
print(input["image_url"])
print(input["lang"])

# You have the input now, do stuff with it
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang=input["lang"], use_gpu=False) # need to run only once to download and load model into memory

result = ocr.ocr(input["image_url"], cls=True)

output = {}
i=0
for line in result:
    output[i] = {"bbox": line[0], "text":line[1][0]}
    i=i+1
    print(line)

print(output)
output = json.dumps(output)

datasets = apify_client.datasets()
if len(datasets.list().items) == 0:
    dataset = apify_client.datasets().get_or_create()
dataset = apify_client.dataset(datasets.list().items[0])

dataset.push_items(output)