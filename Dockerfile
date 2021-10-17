FROM python:3.7

COPY . /app
WORKDIR /app

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install latexmk
RUN apt-get install tesseract-ocr libtesseract-dev libleptonica-dev pkg-config

RUN pip install -r requirements.txt

ENTRYPOINT python main.py
