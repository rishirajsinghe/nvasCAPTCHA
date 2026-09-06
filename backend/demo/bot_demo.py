import asyncio
from playwright.async_api import async_playwright

async def run_bot_demo():
    print("========================================")
    print("        NVAS CAPTCHA BOT DEMO           ")
    print("========================================")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("[*] Opening frontend at http://127.0.0.1:5500")
        try:
            await page.goto("http://127.0.0.1:5500")
            # DO NOT sleep here. Start interacting instantly to keep pageTime very small
            
            print("[*] Simulating high-speed automated bot behavior...")
            
            # Massive unnatural scrolling and jitter
            for i in range(1, 5):
                await page.mouse.move(i * 150, i * 150, steps=1)
            
            # Type Aadhaar unnaturally fast
            await page.focus("#aadhaar-number")
            await page.keyboard.type("123456789012" * 5, delay=1) # 60 chars instantly
            
            # Spam click the input field (extremely high interaction rate)
            for _ in range(30):
                await page.click("#aadhaar-number", delay=5)
            
            # Click Login
            print("[*] Clicking Login to trigger NVAS Verification...")
            await page.click("#login-btn")
            
            # Wait for the backend response to populate the debug container
            print("[*] Waiting for backend ML V4 decision...")
            await page.wait_for_function("() => { const txt = document.body.innerText; return txt.includes('Action:') && txt.includes('Risk Score:'); }", timeout=5000)
            
            # Extract values from the DOM
            page_text = await page.evaluate("document.body.innerText")
            
            risk_score = "N/A"
            action = "N/A"
            model = "N/A"
            
            for line in page_text.split('\n'):
                if line.startswith("Risk Score:"):
                    risk_score = line.split("Risk Score:")[1].strip()
                elif line.startswith("Action:"):
                    action = line.split("Action:")[1].strip()
                elif line.startswith("Model:"):
                    model = line.split("Model:")[1].strip()
            
            print("\n========================================")
            print("        NVAS CAPTCHA BOT DEMO           ")
            print("========================================")
            print("Mode:           AUTOMATED BOT")
            print(f"Risk Score:     {risk_score}")
            print(f"ML Model:       {model}")
            print(f"Decision:       {action}")
            print("========================================")
            
            if model != "ml-v4":
                print(f"[!] WARNING: Expected model ml-v4 but got {model}")
                
            print("\nLeaving browser open for 15 seconds to observe the result...")
            await asyncio.sleep(15)
            
        except Exception as e:
            print(f"Error during bot demo: {e}")
        finally:
            await context.close()
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_bot_demo())
