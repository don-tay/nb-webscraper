# NB Web scraper

Schedulable web scraping tool in Python + Selenium.

## Pre-requisite

- Python 3.9+

## First-time setup

1. Duplicate `.env.example` and rename it to `.env`
2. Fill `.env` with appropriate values
3. On the terminal in the repo's directory, enter the following:

```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the app

```bash
# Mac/Linux
source venv/bin/activate
python3 webscraper.py
```

> NB: Specific fields in web scraper may need to be configured due to platform differences , these fields have been highlighted in the code comments.
