from __future__ import annotations

import asyncio
import os
import time

from ..config import Settings

try:
    from selenium import webdriver  # type: ignore
    from selenium.webdriver.chrome.options import Options  # type: ignore
    from selenium.webdriver.chrome.service import Service  # type: ignore
    from selenium.webdriver.common.by import By  # type: ignore
    from selenium.webdriver.support import expected_conditions as EC  # type: ignore
    from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
except Exception:  # pragma: no cover
    webdriver = None
    Options = None
    Service = None
    By = None
    EC = None
    WebDriverWait = None


class PowerBIRenderClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _make_driver(self):
        if webdriver is None or Options is None:
            raise RuntimeError("selenium is not installed")

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        if self.settings.selenium_hub_url:
            return webdriver.Remote(  # type: ignore[operator]
                command_executor=self.settings.selenium_hub_url,
                options=options,
            )

        if self.settings.chromedriver_path and os.path.exists(self.settings.chromedriver_path):
            service = Service(executable_path=self.settings.chromedriver_path)
            return webdriver.Chrome(service=service, options=options)  # type: ignore[operator]

        return webdriver.Chrome(options=options)  # type: ignore[operator]

    async def render_report(self, report_url: str, target_xpath: str = "") -> bytes:
        return await asyncio.to_thread(self._render_report_sync, report_url, target_xpath)

    def _render_report_sync(self, report_url: str, target_xpath: str) -> bytes:
        driver = self._make_driver()
        try:
            driver.get(report_url)
            time.sleep(max(1, self.settings.render_wait_seconds))

            if target_xpath and WebDriverWait is not None and EC is not None and By is not None:
                try:
                    elem = WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.XPATH, target_xpath))
                    )
                    return elem.screenshot_as_png
                except Exception:
                    pass

            return driver.get_screenshot_as_png()
        finally:
            driver.quit()
