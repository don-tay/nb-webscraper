FROM python:3.9-slim

WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt

RUN apt update && apt install -y chromium-driver

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY webscraper.py ./webscraper.py

CMD ["python", "./webscraper.py"]
