# NB Web scraper

Schedulable web scraping tool in Python + Selenium.

## Pre-requisite

- Python 3.9+
- Docker (recommended)
- For manual run (ie. without Docker), install [ChromeDriver](https://chromedriver.chromium.org/downloads) (or [webdriver_manager](https://pypi.org/project/webdriver-manager/))

## First-time setup

1. Duplicate `.env.example` and rename it to `.env`
2. Fill `.env` with appropriate values
3. (For manual run) On the terminal in the repo's directory, enter the following:

```bash
# Manual run on Mac/Linux
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the app

```bash
# Run with docker (recommended)
./bootstrap.sh

# Manual run on Mac/Linux
source venv/bin/activate
python3 webscraper.py
```

> NB: For manual run, specific fields in web scraper may need to be configured due to platform differences. These fields have been highlighted in the code comments.
