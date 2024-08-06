# Data Scraper Tool for Company Information

Extracts entities' Crunchbase, LinkedIn, and website info into JSON files which will be fed into LLM data structuring system.

## Requirements

- Python 3.7+
- Zyte API key and proxy key
- Chromedriver (setup needed, instructions below)

## Setup

1. Clone the repository and navigate into the project directory:

```
git clone https://github.com/otonomee/resonance-scraper.git
cd resonance-scraper
```

2. Install the required packages: `pip install -r requirements.txt`

3. Set the required environment variables (replace "your-zyte-api-key" and "your-zyte-proxy-key" with your actual keys)

```
export ZYTE_API_KEY="your-zyte-api-key"
export ZYTE_PROXY_KEY="your-zyte-proxy-key"
```

## Running the scrapers

```
# root level directory
python main.py
```

## Next Steps

With these JSON files created for each company from each source, we will then migrate these over to the LLM codebase.
