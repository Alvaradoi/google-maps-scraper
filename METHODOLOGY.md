# Methodology & Architecture Reasoning

## 1. Source Selection: Google Maps vs. Static Directories
Google Maps serves as the most frequently updated and universally validated directory of local businesses globally. Unlike static directories (such as Yelp or YellowPages), Google Maps is natively integrated into consumer navigation and behavior. Consequently, business owners prioritize updating their Google Business Profile over other platforms, resulting in the highest fidelity data for B2B lead generation.

## 2. Technical Approach: Playwright vs. Standard HTTP Requests
Google Maps relies heavily on client-side rendering (CSR) and complex dynamic XHR endpoints protected by evolving tokens (e.g., Protobuf data streams). Standard HTTP requests using libraries like `requests` and `BeautifulSoup` are ineffective because the initial HTML payload contains no business data.

**The "Two-Phase Extraction" Architecture**
To combat Google's aggressive anti-scraping measures (such as randomized and hashed CSS classes), this tool utilizes an asynchronous Playwright engine with a resilient two-phase strategy:
1. **Phase 1 (The Feed Scroll):** The browser scrolls the infinite-loading results feed, extracting only the highly stable `aria-label` (business name) and direct Map URL from the anchor tags.
2. **Phase 2 (The Detail Routing):** The scraper opens a secondary, hidden tab to visit each business's specific URL directly. It extracts rich data (address, website, phone, rating) using Google's reliable accessibility `data-item-id` attributes rather than brittle layout classes. 

## 3. Rate Limiting and Proxy Strategy
Aggressive scraping leads to IP bans and DOM detachment. This tool enforces a native `--delay` flag. By defaulting to a wait state between layout shifts, clicks, and page loads, we simulate organic human reading patterns. For production-scale use, the Playwright context is configured to optionally inject residential proxy credentials, distributing requests across different IPs to avoid Google's rate-limiting triggers.

## 4. Data Validation Pipeline
Data extracted from dynamic DOMs is notoriously messy. We utilize `pydantic.BaseModel` to cast and validate types on the fly. 
* If a rating element reads `4.8 stars`, the extractor regex cleans it and Pydantic enforces it as a `float`. 
* Missing nodes default safely to Python `None` types instead of throwing `IndexError` exceptions, ensuring that our CSV and XLSX exports are clean, structured, and predictable.

## 5. Email Discovery Methodology
Google Maps does not explicitly publicize email addresses to prevent spam. The `--enrich-emails` architecture operates a supplementary web crawl:
1. Extract the `website` URL from the Maps listing.
2. Initialize a new Playwright tab to load the target domain's homepage, followed by its `/contact` path. 
3. Run an optimized regex compiler to locate mail-to strings, explicitly filtering out image artifacts (`.png`, `.webp`) and generic trap accounts (`noreply@`). 
If an email is successfully scraped directly from the domain attached to the listing, the schema assigns a `confidence_score` of `high`.

## 6. Legal & GDPR Framework
This tool strictly scrapes **publicly available contact information**. It does not break encryption, bypass CAPTCHAs, or bypass login screens. Under GDPR, the scraping of B2B contact information for legitimate interest can be permissible, provided the subsequent data processing (such as sales outreach) complies with consent and opt-out laws. Users of this tool act as the Data Controllers and must maintain their own compliance.

