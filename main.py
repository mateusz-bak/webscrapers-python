from bs4 import BeautifulSoup
import json
import urllib.request
import os
import datetime
import time


def send_notification_ad(ad, category):
    msg = "stalowemiasto.pl - " + category + "\n"
    msg += ad["title"] + "\n"
    msg += ad["price"] + "\n"
    msg += ad["url"] + "\n"
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


def download_website(category):
    if category == "działki":
        url = "https://stalowemiasto.pl//ogloszenia/stalowa_wola/ogloszenia.php?mode=pokaz_ogloszenia&id=53&"
    elif category == "domy":
        url = "https://stalowemiasto.pl//ogloszenia/stalowa_wola/ogloszenia.php?mode=pokaz_ogloszenia&id=52&"

    urllib.request.urlretrieve(url, f'{category}.html')


def modify_ad_dict(ad, new_ads):
    ad_dict = {}
    if ad.find('a', class_="oglTytul") is not None:
        ad_dict['title'] = ad.find('a', class_="oglTytul").text
        ad_dict['price'] = ad.find('span',
                                   style="font-size:12px;font-weight:bold;color:#414141;position:absolute;"
                                         "top:48px;right:20px").text
        url = "https://stalowemiasto.pl//ogloszenia/stalowa_wola" + ad.find_all('a', href=True)[1]['href'][1:]
        ad_dict['url'] = url
        new_ads.append(ad_dict)
    return new_ads


def main():
    categories = [
        "działki",
        "domy"
    ]

    for category in categories:
        download_website(category)
        with open(f'{category}.html', 'r') as html_file:
            content = html_file.read()

            soup = BeautifulSoup(content, 'html.parser')
            div_tags = soup.find_all('div', onmouseout="this.style.backgroundColor='#FFF'")

            new_ads = []
            for i in div_tags:
                new_ads = modify_ad_dict(i, new_ads)
            new_ads.reverse()

            try:
                with open(f'{category}.json', 'r') as fin:
                    old_ads = json.load(fin)

                    if old_ads is not None:
                        for new_ad in new_ads:
                            if new_ad not in old_ads:
                                send_notification_ad(new_ad, category)
                                old_ads.append(new_ad)
                                time.sleep(10)

                        with open(f'{category}.json', 'w') as fout:
                            json.dump(old_ads, fout)
            except IOError as e:
                send_notification_error(e)
                try:
                    with open(f'{category}.json', 'w') as fout:
                        json.dump(new_ads, fout)
                except IOError as e:
                    send_notification_error(e)


if __name__ == "__main__":
    main()
