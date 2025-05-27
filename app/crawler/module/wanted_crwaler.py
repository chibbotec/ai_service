from bs4 import BeautifulSoup
import re
import json

def _extract_json_raw_text(soup):
    """JSON에서 모든 텍스트 내용을 raw로 추출"""
    try:
        json_script = soup.find('script', {'id': '__NEXT_DATA__'})
        if json_script:
            data = json.loads(json_script.string)
            initial_data = data.get('props', {}).get('pageProps', {}).get('initialData', {})
            
            if initial_data:
                # 모든 텍스트 필드를 그냥 이어붙이기
                all_text = []
                
                def extract_all_strings(obj):
                    if isinstance(obj, str):
                        all_text.append(obj)
                    elif isinstance(obj, dict):
                        for value in obj.values():
                            extract_all_strings(value)
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_all_strings(item)
                
                extract_all_strings(initial_data)
                
                # 모든 텍스트를 합쳐서 반환
                raw_text = ' '.join(all_text)
                raw_text = re.sub(r'\s+', ' ', raw_text)
                return raw_text.strip()
                
    except Exception as e:
        print(f"JSON 추출 오류: {e}")
            
    return None

def extract_raw_data(html: str, url: str) -> dict:
    """원티드에서 raw 데이터 추출"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # JSON에서 raw 텍스트만 추출
    json_text = _extract_json_raw_text(soup)
    if json_text:
        return {
            'site': 'wanted',
            'url': url,
            'status': 'success',
            'raw_data': json_text
        }
    
    # JSON 실패시 HTML에서 raw 텍스트 추출
    for tag in soup(["script", "style", "noscript", "nav", "footer", "aside"]):
        tag.decompose()
    
    main = soup.find('main') or soup.find('body')
    
    if main:
        text = main.get_text()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        
        return {
            'site': 'wanted',
            'url': url,
            'status': 'success',
            'raw_data': text
        }
    
    return {
        'site': 'wanted',
        'url': url,
        'status': 'error',
        'message': '콘텐츠를 찾을 수 없습니다.'
    }
