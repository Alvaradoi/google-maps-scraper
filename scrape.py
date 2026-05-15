import asyncio
import argparse
from loguru import logger

from scraper.browser import get_browser_context
from scraper.extractor import scrape_maps_leads, enrich_emails
from scraper.exporter import export_data

async def main():
    parser = argparse.ArgumentParser(description="Google Maps B2B Lead Scraper")
    parser.add_argument("--query", type=str, required=True, help="Search query (e.g., 'accountants')")
    parser.add_argument("--location", type=str, required=True, help="Target location (e.g., 'Seattle, WA')")
    parser.add_argument("--limit", type=int, default=50, help="Maximum number of leads to scrape")
    parser.add_argument("--delay", type=float, default=1.5, help="Delay between actions in seconds")
    parser.add_argument("--export-format", type=str, choices=["csv", "xlsx"], default="csv", help="Output format")
    parser.add_argument("--headless", type=str, default="true", help="Run browser in headless mode (true/false)")
    parser.add_argument("--enrich-emails", action="store_true", help="Opt-in flag to visit websites and scrape emails")
    
    args = parser.parse_args()
    
    is_headless = args.headless.lower() == "true"
    
    logger.info(f"Starting scraper: {args.query} in {args.location} (Limit: {args.limit})")
    
    async with get_browser_context(headless=is_headless) as (page, context):
        leads = await scrape_maps_leads(
            page=page, 
            query=args.query, 
            location=args.location, 
            limit=args.limit, 
            delay=args.delay
        )
        
        if args.enrich_emails and leads:
            leads = await enrich_emails(context, leads, args.delay)
            
    export_data(leads, args.query, args.location, args.export_format)
    logger.success("Scraping task completed.")

if __name__ == "__main__":
    asyncio.run(main())

