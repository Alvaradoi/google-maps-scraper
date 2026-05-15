# Google Maps B2B Lead Scraper

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Playwright](https://img.shields.io/badge/Playwright-Async-green)
![Pandas](https://img.shields.io/badge/Pandas-Data-yellow)

A production-grade, asynchronous Python scraper for extracting local business data from Google Maps. Built for B2B lead generation, it emphasizes data integrity, stealthy browser automation utilizing a resilient Two-Phase extraction strategy, and reliable Pydantic schema validation.

## Features
* **Asynchronous Playwright Engine:** Fast, concurrent browsing utilizing async/await patterns.
* **Two-Phase Extraction Architecture:** Bypasses Google's brittle randomized CSS classes by scrolling to collect raw Map URLs, then visiting detail pages to extract highly stable accessibility data attributes.
* **Strict Schema Validation:** Utilizes Pydantic to ensure all exports are clean, typed, and predictable.
* **Email Discovery Pass:** Optional deep-crawl to visit business websites and parse routing/contact pages for direct email contacts.
* **Multi-Format Export:** Exports clean data to CSV or paginated XLSX (including job metadata).
* **Native Proxy Support:** Drop-in support for rotating residential proxies to bypass rate limits.

## Installation
Ensure you have Python 3.11+ installed. 

```bash
git clone https://github.com/yourusername/google-maps-scraper.git
cd google-maps-scraper
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

pip install -r requirements.txt
playwright install chromium
```

## Configuration
For production-scale scraping, configure a residential proxy to avoid IP bans. Create a `.env` file in your root directory based on `.env.example`:

```env
PROXY_SERVER=http://your-proxy-provider.com:7777
PROXY_USERNAME=your_username
PROXY_PASSWORD=your_password
```
*(If no proxy is configured, the scraper will seamlessly default to your local network).*

## Usage Examples

**1. Basic CSV Scrape (Headless)**
```bash
python scrape.py --query "accountants" --location "Seattle, WA" --limit 50
```

**2. Excel Export with Visual Browser Tracking**
```bash
python scrape.py --query "plumbers" --location "Austin, TX" --limit 100 --export-format xlsx --headless false
```

**3. Deep Scrape with Email Enrichment**
```bash
python scrape.py --query "marketing agencies" --location "London, UK" --limit 25 --delay 2 --enrich-emails
```

## Output Format 
The tool outputs tabular data where missing values are strictly handled as `null` (or empty cells). 

| name | category | website | email | rating | review_count | confidence_score |
|---|---|---|---|---|---|---|
| Apex Accounting | Certified Public Accountant | `https://apex.xyz` | info@apex.xyz | 4.8 | 112 | high |
| Smith Bros | Tax Preparation | None | None | 4.1 | 15 | low |

## Use Cases
- **B2B Lead Generation:** Populate CRM systems with fresh, hyper-local business contacts.
- **Competitive Analysis:** Map out competitor density and review ratings in specific municipal zones.
- **Local Market Research:** Evaluate saturated vs. underserved service sectors.
- **Sales Prospecting:** Automate outreach workflows with discovered emails and phone numbers.

## Legal & Compliance
This software is intended for educational and portfolio purposes. 
* It interacts only with publicly accessible web data.
* It does not bypass CAPTCHAs, authentication walls, or attempt malicious intrusion.
* Users must implement their own proxy rotation and rate limiting strategies (via `--delay`) to respect target servers.
* Ensure your usage complies with local laws regarding web scraping and GDPR (e.g., handling discovered email addresses).

