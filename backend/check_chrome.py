import os

def test_chrome():
    from DrissionPage import ChromiumPage, ChromiumOptions
    
    # 1. Check if Chrome exists
    chrome_path = '/usr/bin/google-chrome'
    if not os.path.exists(chrome_path):
        print(f"❌ [에러] 크롬이 {chrome_path} 에 설치되어 있지 않습니다!")
        return
        
    print(f"✅ 구글 크롬 설치 확인됨: {chrome_path}")
    
    # 2. Try launching Chrome with exact backend settings
    print("⏳ DrissionPage 브라우저 런칭 시도 중...")
    try:
        co = ChromiumOptions()
        co.auto_port()
        co.set_browser_path(chrome_path)
        # 헤드리스 모드를 완전히 끕니다! (XVFB 가상 모니터 위에서 돌아가게 만듦)
        co.set_argument('--window-size=1920,1080')
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-gpu')
        co.set_argument('--disable-dev-shm-usage')
        
        page = ChromiumPage(addr_or_opts=co)
        print("✅ 브라우저 성공적으로 켜짐! 사이트 접속 시도...")
        page.get('https://www.jinair.com/promotion/inprogressEvent')
        import time
        time.sleep(3)
        print(f"✅ 페이지 로딩 성공. 타이틀: {page.title}")
        page.quit()
        print("✅ 모든 테스트 통과!")
    except Exception as e:
        print(f"❌ [치명적 에러] 브라우저가 강제로 종료되었습니다. 원인:\n{e}")

if __name__ == "__main__":
    test_chrome()
