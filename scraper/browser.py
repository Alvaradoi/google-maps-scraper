import os
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from loguru import logger

@asynccontextmanager
async def get_browser_context(headless: bool = True):
    """
    Asynchronous context manager to yield a Playwright page.
    Includes proxy support if PROXY_SERVER is defined in the environment.
    """
    playwright = await async_playwright().start()
    
    # Configure the proxy dictionary if credentials exist in the .env file
    proxy_config = None
    proxy_server = os.getenv("PROXY_SERVER")
    if proxy_server:
        proxy_config = {
            "server": proxy_server,
            "username": os.getenv("PROXY_USERNAME", ""),
            "password": os.getenv("PROXY_PASSWORD", "")
        }
        logger.info("Proxy configuration loaded.")

    browser: Browser = await playwright.chromium.launch(
        headless=headless,
        args=["--disable-blink-features=AutomationControlled"],
        proxy=proxy_config  # Inject the proxy at the browser level
    )
    
    context: BrowserContext = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    page: Page = await context.new_page()
    
    try:
        yield page, context
    except Exception as e:
        logger.error(f"Browser execution error: {e}")
        raise
    finally:
        logger.info("Closing browser context.")
        await context.close()
        await browser.close()
        await playwright.stop()

