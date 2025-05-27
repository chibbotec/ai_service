import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import re
from .module.jumpit_crwaler import extract_raw_data as jumpit_extract
from .module.saramin_crwaler import extract_raw_data as saramin_extract
from .module.jobkorea_crwaler import extract_raw_data as jobkorea_extract
from .module.wanted_crwaler import extract_raw_data as wanted_extract
from .module.greetingHR_crwaler import extract_raw_data as greetinghr_extract

class JobCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_site_name(self, url):
        """URL에서 사이트명 추출"""
        domain = urlparse(url).netloc.lower()
        
        if 'jumpit' in domain:
            return 'jumpit'
        elif 'saramin' in domain:
            return 'saramin'
        elif 'jobkorea' in domain:
            return 'jobkorea'
        elif 'wanted' in domain:
            return 'wanted'
        elif 'programmers' in domain:
            return 'programmers'
        elif 'greetinghr.com' in domain:
            return 'greetinghr'
        else:
            return None
    
    def fetch_html(self, url):
        """HTML 가져오기"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"HTML 가져오기 실패: {e}")
            return None
    
    def crawl(self, url):
        """메인 크롤링 함수"""
        print(f"크롤링 시작: {url}")
        
        # 사이트 구분
        site_name = self.get_site_name(url)
        if not site_name:
            return {
                'status': 'error',
                'message': f'지원하지 않는 사이트입니다. 현재 지원하는 사이트: Jumpit, Saramin, JobKorea, Wanted, Programmers, GreetingHR',
                'url': url
            }
        
        print(f"사이트: {site_name}")
        
        # HTML 가져오기
        html = self.fetch_html(url)
        if not html:
            return {
                'status': 'error',
                'message': '해당 URL에서 데이터를 불러올 수 없습니다.',
                'url': url
            }
        
        # 사이트별 크롤링 모듈 호출
        result = self.crawl_by_site(site_name, html, url)
        return result
    
    def crawl_by_site(self, site_name, html, url):
        """사이트별 크롤링 모듈 호출"""
        print(f"{site_name} 전용 크롤링 실행")
        
        if site_name == 'jumpit':
            return jumpit_extract(html, url)
        elif site_name == 'saramin':
            return saramin_extract(html, url)
        elif site_name == 'jobkorea':
            return jobkorea_extract(html, url)
        elif site_name == 'wanted':
            return wanted_extract(html, url)
        elif site_name == 'greetinghr':
            return greetinghr_extract(html, url)
        else:
            return {
                'site': site_name,
                'url': url,
                'status': 'error',
                'message': f'{site_name} 크롤러가 아직 구현되지 않았습니다.'
            }

# =========================
# 사용 함수
# =========================
def crawl_url(url):
    """URL을 입력받아서 크롤링"""
    crawler = JobCrawler()
    result = crawler.crawl(url)
    return result

# if __name__ == "__main__":
#     # URL 입력받기
#     # url = "https://jumpit.saramin.co.kr/position/50843"
#     # url = "https://www.wanted.co.kr/wd/283067"
#     # url = "https://www.wanted.co.kr/wd/284408"
#     # url = "https://www.jobkorea.co.kr/Recruit/GI_Read/46733476?Oem_Code=C1&logpath=1&stext=%EB%B0%B1%EC%97%94%EB%93%9C&listno=1&sc=632"
#     # url = "https://www.jobkorea.co.kr/Recruit/GI_Read/46921467?Oem_Code=C1&logpath=1&stext=%EB%B0%B1%EC%97%94%EB%93%9C&listno=3&sc=631"
#     # url = "https://www.jobkorea.co.kr/Recruit/GI_Read/46940600?Oem_Code=C1&logpath=1&stext=%EB%B0%B1%EC%97%94%EB%93%9C&listno=4&sc=631"
#     url = "https://wefuncorp.career.greetinghr.com/ko/o/91685"
#     if url:
#         result = crawl_url(url)
#         print("=" * 60)
#         print("결과:")
#         if result['status'] == 'success':
#             print(f"사이트: {result['site']}")
#             print(f"URL: {result['url']}")
#             print("Raw 데이터:")
#             print(result['raw_data'])
#         else:
#             print(f"오류: {result.get('message', '알 수 없는 오류')}")
#     else:
#         print("URL이 입력되지 않았습니다.")