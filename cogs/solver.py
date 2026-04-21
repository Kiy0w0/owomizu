   

import asyncio
import os
from discord.ext import commands

try:
    from playwright.async_api import async_playwright
    from playwright_stealth import stealth_async
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class CaptchaSolver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.solving = False

    async def cog_load(self):
        if not PLAYWRIGHT_AVAILABLE:
            await self.bot.log("⚠️ Playwright not installed! Browser Solver disabled.", "#ff9800")
            return

        await self.bot.log("🧩 Browser Solver Ready! (Waiting for trigger)", "#00bcd4")

    async def solve_captcha(self, url, token):
        if self.solving:
            return False

        self.solving = True
        await self.bot.log("🚀 Launching Browser to solve captcha...", "#00bcd4")
        self.bot.add_dashboard_log("captcha", "Launching browser solver...", "info")

        try:
            async with async_playwright() as p:
                await self.bot.log("🧩 Launching Browser (Safe Mode)...", "#b388ff")

                current_dir = os.getcwd()
                browser = await p.chromium.launch_persistent_context(
                    user_data_dir=os.path.join(current_dir, "utils", "browser_profile"),
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"]
                )

                page = browser.pages[0] if browser.pages else await browser.new_page()

                solver_script_path = os.path.join(current_dir, "utils", "solver.js")
                if os.path.exists(solver_script_path):
                    with open(solver_script_path, "r") as f:
                        script_content = f.read()
                    await page.add_init_script(script_content)
                    await self.bot.log("💉 Solver Script Injected!", "#51cf66")

                await self.bot.log("🔑 Authenticating...", "#00bcd4")
                await page.goto("https://discord.com/login")

                script = f"""
                    (function() {{
                        window.t = "{token}";
                        window.localStorage = document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage;
                        window.setInterval(() => window.localStorage.token = `"${{{token}}}"`, 50);
                        window.location.reload();
                    }})();
                """
                await page.evaluate(script)
                await page.wait_for_timeout(3000)

                if "login" in page.url:
                    await self.bot.log("❌ Browser Login Failed (Token might be invalid for browser login)", "#ff4444")
                    await browser.close()
                    self.solving = False
                    return False

                await self.bot.log("🔗 Opening Captcha Link...", "#00bcd4")
                await page.goto(url)

                try:
                    authorize_btn = page.locator("button >> text='Authorize'")
                    if await authorize_btn.count() > 0:
                        await authorize_btn.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass

                await self.bot.log("⏳ Solving challenge...", "#00bcd4")
                await page.wait_for_timeout(5000) 

                try:
                    await page.mouse.click(100, 100)

                    content = await page.content()
                    if "verified" in content.lower() or "thank you" in content.lower():
                        await self.bot.log("✅ Captcha Solved (Auto-Click)!", "#51cf66")
                        self.bot.add_dashboard_log("captcha", "Solved successfully!", "success")
                        await browser.close()
                        self.solving = False
                        return True

                except Exception as e:
                    print(f"Interaction error: {e}")

                await browser.close()

        except Exception as e:
            await self.bot.log(f"💥 Browser Error: {e}", "#c25560")

        self.solving = False
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != self.bot.channel_id:
            return

        if "captcha" in message.content.lower() and "http" in message.content:
            import re
            url_match = re.search(r"(https?://[^\s]+)", message.content)
            if url_match:
                url = url_match.group(1)
                if "owobot.com/captcha" in url:
                    await self.bot.set_stat(False)

                    success = await self.solve_captcha(url, self.bot.token)

                    if success:
                        await self.bot.log("🤖 Auto-Resume after captcha...", "#51cf66")
                        await self.bot.send("owo verify")
                        await asyncio.sleep(2)
                        await self.bot.set_stat(True)
                    else:
                        await self.bot.log("⚠️ Solver Failed - Please solve manually!", "#ff9800")

async def setup(bot):
    await bot.add_cog(CaptchaSolver(bot))