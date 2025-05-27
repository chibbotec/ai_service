from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urljoin

def _fetch_iframe_content(iframe_src, base_url):
    """iframe 내용 가져오기"""
    try:
        # 상대 URL을 절대 URL로 변환
        full_url = urljoin(base_url, iframe_src)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': base_url
        }
        
        response = requests.get(full_url, headers=headers, timeout=10)
        if response.status_code == 200:
            iframe_soup = BeautifulSoup(response.text, 'html.parser')
            
            # iframe 내용에서도 script, style 제거
            for tag in iframe_soup.find_all(["script", "style", "noscript"]):
                tag.decompose()
            
            # body 내용만 추출
            body = iframe_soup.find('body')
            if body:
                return body.get_text(separator=' ')
            else:
                return iframe_soup.get_text(separator=' ')
        else:
            return f"[iframe 로딩 실패: {iframe_src}]"
            
    except Exception as e:
        return f"[iframe 오류: {str(e)}]"

def extract_raw_data(html: str, url: str) -> dict:
    """잡코리아에서 모든 article 태그를 raw 텍스트로 추출 (iframe 내용까지)"""
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
        # 모든 article 태그 찾기
        articles = soup.find_all('article')
        
        if not articles:
            return {
                'site': 'jobkorea',
                'url': url,
                'status': 'error',
                'message': 'article 태그를 찾을 수 없습니다.'
            }
        
        # 모든 article의 텍스트를 하나로 합치기
        raw_text = ""
        
        for article in articles:
            # script, style만 제거
            for tag in article.find_all(["script", "style", "noscript"]):
                tag.decompose()
            
            # iframe 처리 - 실제 내용 가져오기
            for iframe in article.find_all('iframe'):
                iframe_src = iframe.get('src', '')
                if iframe_src:
                    iframe_content = _fetch_iframe_content(iframe_src, url)
                    raw_text += iframe_content + " "
                    # iframe 태그 자체는 제거
                    iframe.decompose()
            
            # 나머지 텍스트 추출 (table 데이터 포함)
            raw_text += article.get_text(separator=' ') + " "
        
        # 공백 정리만
        raw_text = re.sub(r'\s+', ' ', raw_text).strip()
        
        return {
            'site': 'jobkorea',
            'url': url,
            'status': 'success',
            'raw_data': raw_text
        }
        
    except Exception as e:
        return {
            'site': 'jobkorea',
            'url': url,
            'status': 'error',
            'message': f'크롤링 중 오류 발생: {str(e)}'
        }
