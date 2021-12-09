from bs4 import BeautifulSoup
import json
import urllib.request
import os
import datetime
import time


def send_notification(ad):
    msg = ad["ad"] + "\n"
    msg += ad["contact"] + "\n\n"
    msg += datetime.datetime.now().strftime('%d-%m-%Y %H:%M') + "\n\n" + "____________"

    execute_docker(msg)


def execute_docker(msg):
    cmd = f'docker run --rm -d -v /home/mateusz/matrix-commander/data:/data:z matrix-commander  -m "{msg}"'
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

    try:
        with open('ads.json', 'r') as fin:
            old_ads = json.load(fin)
    except IOError:
        old_ads = []

    new_ads.reverse()
    with open('ads.json', 'w') as fout:
        json.dump(new_ads, fout)

    for new_ad in new_ads:
        if new_ad not in old_ads:
            send_notification(new_ad)
            time.sleep(10)


