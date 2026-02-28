import asyncio
import time

async def test_pw():
    print("⏳ Playwright-Stealth 로드 중...")
    try:
        from playwright.async_api import async_playwright
        import playwright_stealth
        print("✅ playwright-stealth 2.0.2 API 목록:")
        print(dir(playwright_stealth))
        
        # Try finding the correct class or function
        if hasattr(playwright_stealth, 'Stealth'):
            print("🚀 'Stealth' 클래스로 진행합니다.")
        elif hasattr(playwright_stealth, 'stealth'):
            print("🚀 'stealth' 함수로 진행합니다.")
            
    except Exception as e:
        import traceback
        print(f"❌ 패키지 로드 실패. 이유:\n{traceback.format_exc()}")
        return

    print("✅ 준비 완료, 브라우저 시작...")
    try:
        async with async_playwright() as p:
            # xvfb 환경이므로 headless=False 로 실행
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--window-size=1920,1080',
                ]
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            # 봇 방어막 우회 플러그인 장착
            import inspect
            if hasattr(playwright_stealth, 'stealth'):
                print("🚀 'stealth' 함수(2.0.2 버전)로 진행합니다.")
                if inspect.iscoroutinefunction(playwright_stealth.stealth):
                    await playwright_stealth.stealth(page)
                else:
                    playwright_stealth.stealth(page)
            else:
                print("❌ stealth 적용 방법을 찾지 못했습니다!")
                return
            await page.goto('https://www.jinair.com/promotion/inprogressEvent')
            
            print("⏳ 로딩 & Cloudflare 우회 대기 (15초)...")
            await asyncio.sleep(15)
            
            title = await page.title()
            print(f"✅ 접속 완료 타이틀: {title}")
            
            source = await page.content()
            if "Attention Required!" in title or "challenge" in source.lower():
                print("❌ 여전히 Cloudflare 봇 검문소에 막혀있습니다!")
            else:
                print("🎉 클라우드플레어 우회 대성공! 진짜 진에어 페이지 로딩됨!")
                
            await browser.close()
            
    except Exception as e:
        print(f"❌ 실행 중 치명적 에러 발생: {e}")

if __name__ == "__main__":
    asyncio.run(test_pw())
