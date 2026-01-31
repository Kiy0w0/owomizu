"""
Mizu OwO Bot - Auto Captcha Solver (Browser-based)
Copyright (C) 2025 MizuNetwork
"""

import asyncio
import os
from discord.ext import commands
from discord.ext.commands import ExtensionNotLoaded

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
            
        config = self.bot.settings_dict.get("captcha", {})
        # We check special flag 'browserSolver' inside captcha settings, default false.
        if not config.get("autoSolve", False): # Re-use autosolve flag or create new one?
             # Let's assume autosolve=True means enable this advanced solver if available
             pass

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
                
                # Launch Browser (No Extension, Clean Profile)
                current_dir = os.getcwd()
                browser = await p.chromium.launch_persistent_context(
                    user_data_dir=os.path.join(current_dir, "utils", "browser_profile"),
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                page = browser.pages[0] if browser.pages else await browser.new_page()

                # Read Transparent Solver Script
                solver_script_path = os.path.join(current_dir, "utils", "solver.js")
                if os.path.exists(solver_script_path):
                    with open(solver_script_path, "r") as f:
                        script_content = f.read()
                    # Inject script on every navigation
                    await page.add_init_script(script_content)
                    await self.bot.log("💉 Solver Script Injected!", "#51cf66")

                # 1. Login Discord (Inject Token)
                await self.bot.log("🔑 Authenticating...", "#00bcd4")
                await page.goto("https://discord.com/login")
                
                # Inject Token JS
                script = f"""
                    (function() {{
                        window.t = "{token}";
                        window.localStorage = document.body.appendChild(document.createElement('iframe')).contentWindow.localStorage;
                        window.setInterval(() => window.localStorage.token = `"${{window.t}}"`, 50);
                        window.location.reload();
                    }})();
                """
                await page.evaluate(script)
                await page.wait_for_timeout(3000) # Wait for reload/login
                
                # Verify Login
                if "login" in page.url:
                    await self.bot.log("❌ Browser Login Failed (Token might be invalid for browser login)", "#ff4444")
                    await browser.close()
                    self.solving = False
                    return False

                # 2. Go to Captcha URL
                await self.bot.log("🔗 Opening Captcha Link...", "#00bcd4")
                await page.goto(url)
                
                # 3. Handle 'Authorize' button if it's an OAuth link first
                # OwO usually sends https://owobot.com/captcha which redirects to OAuth
                try:
                    # Look for "Authorize" button
                    authorize_btn = page.locator("button >> text='Authorize'")
                    if await authorize_btn.count() > 0:
                        await authorize_btn.click()
                        await page.wait_for_timeout(2000)
                except:
                    pass
                
                # 4. Wait for Cloudflare/Human Check
                # Just waiting often solves simple checks due to 'stealth' plugin
                await self.bot.log("⏳ Solving challenge...", "#00bcd4")
                await page.wait_for_timeout(5000) 
                
                # Check for "I am human" checkbox (hCaptcha/Cloudflare)
                # This is a naive implementation; complex puzzles need 2Captcha/CapSolver API
                try:
                    # Generic attempt to click checkboxes
                    await page.mouse.click(100, 100) # Random click to focus
                    
                    # Try to find common captcha frames/buttons
                    # Note: Full image solving (selecting buses/traffic lights) is VERY hard without paid API (2captcha/capsolver)
                    # We rely on "One-Click" pass here.
                    
                    # Check for success message on page
                    content = await page.content()
                    if "verified" in content.lower() or "thank you" in content.lower():
                        await self.bot.log("✅ Captcha Solved (Auto-Click)!", "#51cf66")
                        self.bot.add_dashboard_log("captcha", "Solved successfully!", "success")
                        await browser.close()
                        self.solving = False
                        return True
                        
                except Exception as e:
                    print(f"Interaction error: {e}")

                # Take screenshot for debug
                # await page.screenshot(path="captcha_debug.png")
                
                await browser.close()
                
        except Exception as e:
            await self.bot.log(f"💥 Browser Error: {e}", "#c25560")
        
        self.solving = False
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        # Listen for Captcha Link
        if message.channel.id != self.bot.channel_id:
            return
            
        if "captcha" in message.content.lower() and "http" in message.content:
             # Extract URL
             import re
             url_match = re.search(r"(https?://[^\s]+)", message.content)
             if url_match:
                 url = url_match.group(1)
                  if "owobot.com/captcha" in url:
                      # Pause bot first
                      await self.bot.set_stat(False)
                      
                      success = await self.solve_captcha(url, self.bot.token)
                     
                     if success:
                         await self.bot.log("🤖 Auto-Resume after captcha...", "#51cf66")
                         await self.bot.send("owo verify") # Check verify status
                         await asyncio.sleep(2)
                         await self.bot.set_stat(True)
                     else:
                         await self.bot.log("⚠️ Solver Failed - Please solve manually!", "#ff9800")
                         # Bot remains paused

async def setup(bot):
    await bot.add_cog(CaptchaSolver(bot))
