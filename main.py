from bs4 import BeautifulSoup
import json
import urllib.request
import os
import datetime
import time


def send_notification_ad(ad):
    msg = "stalowka.net" + "\n"
    msg += ad["ad"] + "\n"
    msg += ad["contact"] + "\n"
    msg += datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
    execute_docker(msg)


def send_notification_error(e):
    msg = str(e) + "\n"
    msg += str(e.args) + "\n"
    msg += datetime.datetime.now().strftime('%d-%m-%Y %H:%M') + "\n" + "____________"
    execute_docker(msg)


def execute_docker(msg):
    cmd = f'docker run --rm -d -v /home/mateusz/matrix-commander/data:/data:z matrix-commander  -m "{msg}"'
    os.system(cmd)


def download_website():
    url = "https://www.stalowka.net/stalowa-wola/ogloszenia_5.html"
    urllib.request.urlretrieve(url, "webpage.html")


def modify_ad_dict(ad_box, new_ads):
    ad_parts = ad_box.find_all('span', class_="txt")
    ad_dict = {"ad": ad_parts[0].text, "contact": ad_parts[1].text}
    new_ads.append(ad_dict)
    return new_ads


def main():
    download_website()
    with open('webpage.html', 'r') as html_file:
        content = html_file.read()

        soup = BeautifulSoup(content, 'html.parser')
        span_tags = soup.find_all('td')

        ads_section = span_tags[89].td
        ads_boxes = ads_section.find_all('td', width="460", align="left")
        new_ads = []

        for ad_box in ads_boxes[::2]:
            new_ads = modify_ad_dict(ad_box, new_ads)
        new_ads.reverse()

        try:
            with open('ads.json', 'r') as fin:
                old_ads = json.load(fin)

                for new_ad in new_ads:
                    if new_ad not in old_ads:
                        send_notification_ad(new_ad)
                        old_ads.append(new_ad)
                        time.sleep(10)

                with open('ads.json', 'w') as fout:
                    json.dump(old_ads, fout)
        except IOError as e:
            send_notification_error(e)
            try:
                with open('ads.json', 'w') as fout:
                    json.dump(new_ads, fout)
            except IOError as e:
                send_notification_error(e)


if __name__ == "__main__":
    main()
