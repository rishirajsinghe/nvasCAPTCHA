import asyncio
from playwright.async_api import async_playwright

async def run_human_demo():
    print("========================================")
    print("        NVAS CAPTCHA HUMAN DEMO           ")
    print("========================================")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()
        
        # Navigate to the frontend
        print("[*] Opening frontend at http://127.0.0.1:5500")
        await page.goto("http://127.0.0.1:5500")
        
        # Simulate human typing
        print("[*] Simulating human behavior...")
        await page.mouse.move(500, 300)
        await asyncio.sleep(0.5)
        await page.mouse.move(100, 200, steps=10)
        
        await page.click("#aadhaar-number")
        
        # Type with human-like delays
        aadhaar = "123456789012"
        for char in aadhaar:
            await page.keyboard.press(char, delay=200)
            await asyncio.sleep(0.1)
            
        await asyncio.sleep(2)
        
        # Click login
        print("[*] Clicking Login to trigger NVAS Verification...")
        await page.mouse.move(600, 400, steps=15)
        await asyncio.sleep(0.5)
        await page.mouse.move(800, 600, steps=10)
        await page.click("#login-btn")
        
        print("[*] Waiting for backend ML V4 decision...")
        
        # Wait for either success or CAPTCHA or BLOCK state
        await page.wait_for_selector("#success-state:visible, #captcha-group:visible, #block-state:visible", timeout=15000)
        
        # Extract the decision from the debug info container
        debug_info = await page.locator(".login-card > div:last-child").inner_text()
        
        print("\n========================================")
        print("        NVAS CAPTCHA HUMAN DEMO           ")
        print("========================================")
        print("Mode:           HUMAN")
        
        if "Risk Score:" in debug_info:
            score = debug_info.split("Risk Score:")[1].split("\n")[0].strip()
            print(f"Risk Score:     {score}")
            
        if "Model:" in debug_info:
            model = debug_info.split("Model:")[1].split("\n")[0].strip()
            print(f"ML Model:       {model}")
            
        if "Action:" in debug_info:
            action = debug_info.split("Action:")[1].split("\n")[0].strip()
            print(f"Decision:       {action}")
            
        print("========================================\n")
        
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_human_demo())
