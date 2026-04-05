import asyncio
from playwright.async_api import async_playwright
from typing import Optional, Dict, Any, List
from core.config import ScanContext
from core.log import setup_logger

logger = setup_logger()

class DynamicValidator:
    def __init__(self, context: ScanContext):
        self.context = context

    async def validate(self, url: str, params: Any, payload: str, method: str = "GET") -> bool:
        """
        Actually executes the payload in a real Chromium browser.
        If an alert/confirm/prompt is triggered, the vulnerability is 100% confirmed.
        """
        async with async_playwright() as p:
            # We use a real browser to eliminate false positives
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            # Inject Cookies for Authenticated Validation
            if self.context.config.cookies:
                # Playwright expects a list of cookie objects
                parsed_cookies = []
                for name, value in self.context.config.cookies.items():
                    parsed_cookies.append({
                        "name": name,
                        "value": value,
                        "url": url # Restrict cookie to current URL domain
                    })
                await context.add_cookies(parsed_cookies)

            page = await context.new_page()
            
            # Use custom headers (like Cookies, Auth)
            if self.context.headers:
                await page.set_extra_http_headers(self.context.headers)

            triggered = asyncio.Event()
            # Catching JavaScript dialogs (alert, prompt, confirm)
            page.on("dialog", lambda dialog: triggered.set())
            
            try:
                if method.upper() == "GET":
                    # Construct URL with parameters
                    query = "&".join([f"{k}={v}" for k, v in params.items()]) if isinstance(params, dict) else ""
                    full_url = f"{url}?{query}" if "?" not in url else f"{url}&{query}"
                    await page.goto(full_url, timeout=self.context.config.timeout * 1000)
                else:
                    # For POST, we can't just goto a URL with data. 
                    # We need to use page.evaluate to perform a fetch or form submission.
                    await page.goto(url)
                    # Simple POST simulation via JS
                    await page.evaluate(f"""
                        fetch('{url}', {{
                            method: 'POST',
                            body: '{params}',
                            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }}
                        }}).then(r => r.text()).then(t => document.body.innerHTML = t);
                    """)

                # Wait for the payload to execute (max 3 seconds)
                try:
                    await asyncio.wait_for(triggered.wait(), timeout=3.0)
                    return True
                except asyncio.TimeoutError:
                    return False
            except Exception as e:
                logger.debug(f"Dynamic validation failed for {url}: {e}")
                return False
            finally:
                await browser.close()

def run_dynamic_validation(url: str, params: Any, payload: str, context: ScanContext) -> bool:
    """Synchronous wrapper to run the async validator."""
    validator = DynamicValidator(context)
    try:
        return asyncio.run(validator.validate(url, params, payload))
    except Exception:
        return False
