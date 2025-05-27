from bs4 import BeautifulSoup
import re

def extract_raw_data(html: str, url: str) -> dict:
    """그리팅HR에서 완전한 raw 데이터 추출 (매핑 없음)"""
    soup = BeautifulSoup(html, 'html.parser')
    
    try:
        # 불필요한 태그 제거
        for tag in soup(["script", "style", "noscript", "header", "footer"]):
            tag.decompose()
        
        # body 전체에서 텍스트 추출
        body = soup.find('body')
        if not body:
            return {
                'site': 'greetinghr',
                'url': url,
                'status': 'error',
                'message': 'body 태그를 찾을 수 없습니다.'
            }
        
        # 순수한 텍스트만 추출
        raw_text = body.get_text()
        
        # 공백 정리만
        raw_text = re.sub(r'\s+', ' ', raw_text).strip()
        
        return {
            'site': 'greetinghr',
            'url': url,
            'status': 'success',
            'raw_data': raw_text
        }
        
    except Exception as e:
        return {
            'site': 'greetinghr',
            'url': url,
            'status': 'error',
            'message': f'크롤링 중 오류 발생: {str(e)}'
        }
