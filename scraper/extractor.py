import asyncio
import urllib.parse
import re
from typing import List, Optional
from loguru import logger
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from .validator import BusinessLead, extract_emails

# We only need the feed container and the link element for the scroll phase
SELECTORS = {
    "feed_container": "div[role='feed']",
    "result_item": "a[href*='/maps/place/']",
}

async def scrape_maps_leads(page: Page, query: str, location: str, limit: int, delay: float) -> List[BusinessLead]:
    """
    Two-Phase Extraction:
    1. Scrolls the feed to collect direct URLs for each business.
    2. Opens a new tab to visit each URL and safely extract detailed data points.
    """
    full_query = f"{query} in {location}"
    encoded_query = urllib.parse.quote(full_query)
    search_url = f"https://www.google.com/maps/search/{encoded_query}"
    
    logger.info(f"Navigating directly to Google Maps URL: {search_url}")
    await page.goto(search_url, wait_until="domcontentloaded")
    
    try:
        await page.wait_for_selector(SELECTORS["feed_container"], timeout=15000)
    except PlaywrightTimeoutError:
        logger.error("Could not find search results feed. Rate limited or blocked.")
        return []

    # ==========================================
    # PHASE 1: Collect URLs from the scroll feed
    # ==========================================
    business_links = []  # Store tuples of (name, href)
    processed_urls = set()
    
    logger.info("Phase 1: Scrolling results feed to collect business links...")
    consecutive_empty_scrolls = 0
    
    while len(business_links) < limit and consecutive_empty_scrolls < 5:
        await asyncio.sleep(delay)
        items = await page.locator(SELECTORS["result_item"]).all()
        
        added_in_pass = 0
        for item in items:
            if len(business_links) >= limit:
                break
                
            try:
                name = await item.get_attribute("aria-label")
                href = await item.get_attribute("href")
                
                if not name or not href or href in processed_urls:
                    continue
                    
                processed_urls.add(href)
                business_links.append((name, href))
                added_in_pass += 1
                
            except Exception as e:
                logger.warning(f"Failed to get link attributes: {e}")
                continue

        if added_in_pass == 0:
            consecutive_empty_scrolls += 1
        else:
            consecutive_empty_scrolls = 0
            
        await page.evaluate(f"""
            const feed = document.querySelector("{SELECTORS['feed_container']}");
            if (feed) feed.scrollTop = feed.scrollHeight;
        """)
        
    logger.info(f"Collected {len(business_links)} business URLs. Beginning Phase 2...")

    # ==========================================
    # PHASE 2: Visit each URL to extract details
    # ==========================================
    leads: List[BusinessLead] = []
    
    # Open a dedicated page context so we don't mess up the main feed
    detail_page = await page.context.new_page()
    
    for name, url in business_links:
        logger.info(f"Extracting rich details for: {name}")
        try:
            # Navigate to the specific business detail page
            await detail_page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(delay) # Give the detail pane a moment to fully render
            
            # Using highly stable data-item-id and aria-labels for extraction
            address, website, phone, rating, review_count = None, None, None, None, None
            
            try:
                # Extract Address
                addr_loc = detail_page.locator("button[data-item-id='address']")
                if await addr_loc.count() > 0:
                    val = await addr_loc.first.get_attribute("aria-label")
                    address = val.replace("Address: ", "").strip() if val else None
            except Exception: pass
            
            try:
                # Extract Website URL
                web_loc = detail_page.locator("a[data-item-id='authority']")
                if await web_loc.count() > 0:
                    website = await web_loc.first.get_attribute("href")
            except Exception: pass
            
            try:
                # Extract Phone Number
                phone_loc = detail_page.locator("button[data-item-id^='phone:tel:']")
                if await phone_loc.count() > 0:
                    val = await phone_loc.first.get_attribute("aria-label")
                    phone = val.replace("Phone: ", "").strip() if val else None
            except Exception: pass
            
            try:
                # Extract Rating and Review Count
                rating_loc = detail_page.locator("span[aria-label*='stars']")
                if await rating_loc.count() > 0:
                    aria_label = await rating_loc.first.get_attribute("aria-label")
                    if aria_label:
                        # Regex to pull numbers out of text like "4.8 stars 1,234 Reviews"
                        stars_match = re.search(r"([\d\.]+)\s*stars", aria_label)
                        if stars_match:
                            rating = float(stars_match.group(1))
                        
                        reviews_match = re.search(r"([\d,]+)\s*[Rr]eviews?", aria_label)
                        if reviews_match:
                            review_count = int(reviews_match.group(1).replace(",", ""))
            except Exception: pass
            
            # Build the validated lead
            lead = BusinessLead(
                name=name,
                address=address,
                phone=phone,
                website=website,
                rating=rating,
                review_count=review_count,
                query=full_query
            )
            leads.append(lead)
            logger.debug(f"Success: {name} | Rating: {rating} | Site: {website}")
            
        except Exception as e:
            logger.warning(f"Failed to load details for {name}: {e}")
            # Fallback to appending just the name if the page crashed
            leads.append(BusinessLead(name=name, query=full_query))
            
    # Clean up the detail tab
    await detail_page.close()
    
    logger.info(f"Successfully extracted {len(leads)} comprehensive leads.")
    return leads

async def enrich_emails(context, leads: List[BusinessLead], delay: float) -> List[BusinessLead]:
    """
    Takes a list of leads, and for those with websites, visits the site and /contact page
    to discover email addresses via regex.
    """
    logger.info("Starting email enrichment pass...")
    page = await context.new_page()
    
    for lead in leads:
        if not lead.website:
            continue
            
        logger.info(f"Enriching emails for {lead.name} via {lead.website}")
        try:
            await page.goto(lead.website, timeout=15000, wait_until="domcontentloaded")
            homepage_text = await page.content()
            emails = extract_emails(homepage_text)
            
            if not emails:
                await asyncio.sleep(delay)
                contact_url = lead.website.rstrip('/') + '/contact'
                try:
                    await page.goto(contact_url, timeout=15000, wait_until="domcontentloaded")
                    contact_text = await page.content()
                    emails.update(extract_emails(contact_text))
                except Exception:
                    pass
            
            if emails:
                lead.email = list(emails)[0]
                lead.confidence_score = "high"
                logger.success(f"Found email: {lead.email}")
                
        except Exception as e:
            logger.warning(f"Could not enrich {lead.name}: {e}")
            
        await asyncio.sleep(delay)
        
    await page.close()
    return leads

async def _get_text_or_none(parent, selector: str) -> Optional[str]:
    """Helper to extract text safely without throwing exceptions."""
    try:
        loc = parent.locator(selector).first
        if await loc.is_visible(timeout=500):
            return await loc.inner_text()
    except Exception:
        pass
    return None

