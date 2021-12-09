from bs4 import BeautifulSoup
import json
import urllib.request
import os


def send_notification(ad):
    print(ad["ad"])
    print(ad["contact"])
    cmd = 'docker run --rm -ti -v /home/mateusz/matrix-commander/data:/data:z matrix-commander  -m "test"'
    os.system(cmd)


def download_website():
    url = "https://www.stalowka.net/stalowa-wola/ogloszenia_5.html"
    urllib.request.urlretrieve(url, "webpage.html")


download_website()
with open('webpage.html', 'r') as html_file:
    content = html_file.read()

    soup = BeautifulSoup(content, 'html.parser')
    span_tags = soup.find_all('td')

    ads_section = span_tags[89].td
    ads_boxes = ads_section.find_all('td', width="460", align="left")
    new_ads = []

    for ad_box in ads_boxes[::2]:
        ad_parts = ad_box.find_all('span', class_="txt")
        ad_dict = {"ad": ad_parts[0].text, "contact": ad_parts[1].text}
        new_ads.append(ad_dict)

    with open('ads.json', 'r') as fin:
        old_ads = json.load(fin)

    new_ads.reverse()
    with open('ads.json', 'w') as fout:
        json.dump(new_ads, fout)

    for new_ad in new_ads:
        if new_ad not in old_ads:
            send_notification(new_ad)


