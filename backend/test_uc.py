import time
import os

def test_uc():
    print("⏳ undetected-chromedriver 로드 중...")
    try:
        import undetected_chromedriver as uc
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("❌ undetected-chromedriver 또는 selenium 패키지가 깔려있지 않습니다. pip install undetected-chromedriver selenium 실행 바랍니다.")
        return

    chrome_path = '/usr/bin/google-chrome'
    if not os.path.exists(chrome_path):
        print(f"❌ 구글 크롬 설치 안됨: {chrome_path}")
        return

    print("✅ 준비 완료, 브라우저 시작...")
    try:
        options = uc.ChromeOptions()
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        
        # In xvfb it doesn't need to be headless
        driver = uc.Chrome(
            options=options,
            browser_executable_path=chrome_path,
            use_subprocess=True
        )
        
        print("✅ 브라우저 열림, 진에어 접속 중...")
        driver.get('https://www.jinair.com/promotion/inprogressEvent')
        
        print("⏳ 로딩 & Cloudflare 우회 대기 (15초)...")
        time.sleep(15)
        
        title = driver.title
        print(f"✅ 접속 완료 타이틀: {title}")
        
        source = driver.page_source
        if "Attention Required!" in title or "challenge" in source.lower():
            print("❌ 여전히 Cloudflare 봇 검문소에 막혀있습니다!")
        else:
            print("🎉 클라우드플레어 우회 대성공! 진짜 진에어 페이지 로딩됨!")
            
        driver.quit()
        
    except Exception as e:
        print(f"❌ 실행 중 치명적 에러 발생: {e}")

if __name__ == "__main__":
    test_uc()
