
from bs4 import BeautifulSoup
import requests

hdr = {
'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
'sec-ch-ua-mobile': '?0',
'Upgrade-Insecure-Requests': '1',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
}


def get_img_url(url):
    page = requests.get(url, headers = hdr)

    if(page.status_code != 200):
        print(page.status_code)
        return None
    else:
        try:
            soup = BeautifulSoup(page.content, "html.parser")
            div = soup.find("div", class_="image_content backdrop")
            return "https://www.themoviedb.org" + div.find('img').attrs['data-src']
        except:
            print("img not found!")
            return None
