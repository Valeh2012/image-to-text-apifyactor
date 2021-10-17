# Actor - Image to Text

The actor takes an input image in a specified format (`base64` or `url`) and using asked Optic Character Recognition (OCR) model ([PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) or [Tesseract](https://github.com/tesseract-ocr/)) extracts textual data in required language (See OCR model documentations for available languages). The result is saved into Key-Value store as one of output formats (`pdf`, `txt` or `bbox`)

## INPUT

Input of this actor should be JSON containing filter specification. Allowed filters are:

| Field | Type | Description | Allowed values |
| ----- | ---- | ----------- | -------------- |
| input_type | String | Input image format | `base64` or `url` |
| input_image | String | Image | Any valid string value |
| language | String | Text language | See OCR model documentations (e.g `en`)|
| ocr | String | Specific OCR model | `paddle` or `tesseract` |
| output_format| String | Desired output format | `bbox`/`pdf` for PaddleOCR or `txt`/`pdf` for Tesseract |


## OUTPUT

Once the actor finishes, it will output a textual data in specified format.
 - bbox : list of bounding boxes and text inside
 - pdf : Base64 encoded pdf file
 - txt : String text

## Sample Input
```json
{
    "input_type": "url",
    "input_image": "https://images4.programmersought.com/934/e8/e89758ae0ed991f1c8aba947addec9e6.png",
    "lang": "eng",
    "ocr": "tesseract", 
    "output_format": "bbox" 
}
```

## Sample Output
```json
{
    "response": "Sample PDF Document\n\nRobert Maron\nGrzegorz. Grudziriski\n\nFebruary 20, 1999\n\x0c", 
    "error": None
}
```

