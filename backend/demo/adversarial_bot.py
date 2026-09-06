import asyncio
from playwright.async_api import async_playwright

async def run_adversarial_demo():
    print("========================================")
    print("       NVAS CAPTCHA ADVERSARIAL BOT     ")
    print("========================================")
    print("Target:       http://127.0.0.1:5500/")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = await context.new_page()
        
        # Navigate to the frontend
        print("[*] Opening frontend at http://127.0.0.1:5500/")
        await page.goto("http://127.0.0.1:5500/")
        
        print("[*] Simulating aggressive adversarial bot behavior...")
        
        # Generate extremely rapid interaction and coordinate jumps
        # Jump from extreme corners instantly
        await page.mouse.move(0, 0)
        await page.mouse.move(1920, 1080)
        await page.mouse.move(50, 50)
        
        # Click randomly very fast
        for _ in range(5):
            await page.mouse.click(100, 100)
            
        await page.click("#aadhaar-number")
        
        # Type extremely fast (0 delay between keystrokes)
        aadhaar = "464262562352"
        for char in aadhaar:
            await page.keyboard.press(char, delay=0)
            
        # Rapid focus/blur events
        await page.evaluate("document.getElementById('aadhaar-number').blur()")
        await page.evaluate("document.getElementById('aadhaar-number').focus()")
        
        # Click login immediately without moving mouse gracefully
        print("[*] Clicking Login to trigger NVAS Verification...")
        await page.click("#login-btn", force=True)
        
        print("[*] Waiting for backend ML V4 decision...")
        
        # Wait for either success or CAPTCHA or BLOCK state
        await page.wait_for_selector("#success-state:visible, #captcha-group:visible, #block-state:visible", timeout=15000)
        
        # Extract the decision from the debug info container
        debug_info = await page.locator(".login-card > div:last-child").inner_text()
        
        print("\n========================================")
        print("       NVAS CAPTCHA ADVERSARIAL BOT     ")
        print("========================================")
        print("Target:       http://127.0.0.1:5500/")
        print("Mode:         AUTOMATED ADVERSARIAL BOT")
        
        if "Risk Score:" in debug_info:
            score = debug_info.split("Risk Score:")[1].split("\n")[0].strip()
            print(f"Risk Score:   {score}")
            
        if "Model:" in debug_info:
            model = debug_info.split("Model:")[1].split("\n")[0].strip()
            print(f"ML Model:     {model}")
            
        if "Action:" in debug_info:
            action = debug_info.split("Action:")[1].split("\n")[0].strip()
            print(f"Decision:     {action.upper()}")
            
        print("========================================\n")
        print("The bot interacted with the real NVAS frontend. Behavioral telemetry was collected by the SDK and evaluated by ML V4.\n")
        print("Leaving browser open for 15 seconds to observe the result...")
        
        await asyncio.sleep(15)
        
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_adversarial_demo())
