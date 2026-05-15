import pytest
from scraper.validator import BusinessLead, extract_emails

def test_extract_emails_valid():
    """Test that valid emails are correctly identified from text."""
    text = "Contact us at info@examplebiz.com or support@examplebiz.com."
    emails = extract_emails(text)
    assert "info@examplebiz.com" in emails
    assert "support@examplebiz.com" in emails
    assert len(emails) == 2

def test_extract_emails_ignores_images():
    """Test that regex doesn't match image file extensions."""
    text = "Here is our logo: logo@2x.png. Email us: real@domain.com"
    emails = extract_emails(text)
    assert "logo@2x.png" not in emails
    assert "real@domain.com" in emails

def test_business_lead_validation():
    """Test that the Pydantic schema enforces types and assigns defaults."""
    data = {
        "name": "Acme Corp",
        "query": "tech in NY"
    }
    lead = BusinessLead(**data)
    assert lead.name == "Acme Corp"
    assert lead.category is None  # Defaults to None
    assert lead.confidence_score == "low"  # Default value
    assert lead.email is None

