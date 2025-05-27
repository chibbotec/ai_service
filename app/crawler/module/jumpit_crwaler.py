from bs4 import BeautifulSoup
import re

def extract_raw_data(html: str, url: str) -> dict:
    """점핏에서 raw 데이터 추출"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 불필요한 태그 제거
    for tag in soup(["script", "style", "noscript", "header", "nav", "footer"]):
        tag.decompose()
    
    # 메인 콘텐츠만
    main = soup.find('main') or soup
    
    # 텍스트 추출 및 정리
    text = main.get_text()
    text = re.sub(r'\s+', ' ', text)  # 공백 정리
    text = re.sub(r'\n+', '\n', text)  # 줄바꿈 정리
    
    return {
        'site': 'jumpit',
        'url': url,
        'status': 'success',
        'raw_data': text.strip()
    }
