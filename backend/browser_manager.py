# browser_manager.py

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
import threading


class BrowserManager:
    """
    Singleton manager for Playwright browser instance.
    Ensures only one browser is launched and reused across all scrapers.
    """

    _playwright = None
    _browser: Browser = None
    _lock = threading.Lock()

    @classmethod
    def get_browser(cls) -> Browser:
        """
        Returns a shared Chromium browser instance.
        Launches it if it does not exist.
        """

        if cls._browser is None:
            with cls._lock:
                if cls._browser is None:
                    cls._playwright = sync_playwright().start()

                    cls._browser = cls._playwright.chromium.launch(
                        headless=True,
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--no-sandbox",
                            "--disable-setuid-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-gpu"
                        ]
                    )

        return cls._browser

    @classmethod
    def new_page(cls) -> Page:
        """
        Creates a new page from the shared browser.
        """

        browser = cls.get_browser()

        context: BrowserContext = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800}
        )

        page: Page = context.new_page()

        return page

    @classmethod
    def shutdown(cls):
        """
        Gracefully shuts down the browser and playwright.
        Call when the application exits.
        """

        if cls._browser:
            cls._browser.close()
            cls._browser = None

        if cls._playwright:
            cls._playwright.stop()
            cls._playwright = None