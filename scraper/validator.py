import re
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class BusinessLead(BaseModel):
    """Pydantic model defining the strict schema for a parsed business lead."""
    name: str
    category: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    hours: Optional[str] = None
    source: str = "Google Maps"
    query: str
    scraped_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: str = "low"

def extract_emails(text: str) -> set[str]:
    """
    Extracts valid email addresses from raw text using regex.
    Filters out common image extensions or invalid formats.
    """
    if not text:
        return set()
    
    # Standard email extraction regex
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    raw_emails = set(re.findall(pattern, text))
    
    valid_emails = set()
    # Adjusted ignore patterns to not conflict with common test domains
    ignore_patterns = ['test@', 'noreply', 'no-reply', 'sentry']
    
    for email in raw_emails:
        email_lower = email.lower()
        # Filter obvious non-emails or generic ones if necessary
        if any(ignore in email_lower for ignore in ignore_patterns):
            continue
        if email_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            continue
        valid_emails.add(email_lower)
        
    return valid_emails

