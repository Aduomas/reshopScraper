from requests_html import HTMLSession
import csv
import os
import logging
import configparser
import io
import sys

# make a logger.


def fetch(r):
    items = r.html.xpath('//div[@id="gf-products"]/div')

    sheet = [["Name", "Price", "Link"]]

    for item in items:
        raw_name = item.xpath('//a/text()')
        name = ''
        for s in raw_name:
            if s == '\n':
                continue
            name += s

        link = 'https://reshop.lt' + item.xpath('//a/@href')[0]

        # this check has been implemented in order to not raise errors with prices that have sales next to them
        price_html = item.xpath('//span[@class="spf-product-card__price money"]/text()')
        price = None
        if price_html:
            price = price_html[0]
        else:
            price = item.xpath('//span[@class="spf-product-card__saleprice money"]/text()')[0]
        
        sheet.append([name, price, link])
    return sheet


def isIdentical(oldSheet, newSheet):
    if oldSheet != newSheet:
        print("something has changed!")
        return False
    print("no changes found")
    return True

def exportData(sheet, fileName):
    with open(fileName, "w", newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(sheet)

def update(file_name, sheet):
    if os.path.isfile(file_name):
        with open(file_name, "r", encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            oldSheet = []
            for line in reader:
                oldSheet.append(line)
            # slow algorithm
            if not isIdentical(oldSheet, sheet):
                list_difference = [item for item in sheet if item not in oldSheet]
                if list_difference:
                    print("added: \n", list_difference[0]) # what's new only, not what's removed tho.
                else:
                    list_difference = [item for item in oldSheet if item not in sheet]
                    if list_difference:
                        print("removed: \n", list_difference[0])
    else:
        exportData(sheet, file_name)
        print(f"exported data into {file_name}")

urls = [
    'https://reshop.lt/collections/klaviaturos',
    'https://reshop.lt/collections/pelytes',
    'https://reshop.lt/collections/ausines?limit=100'
]
print(os.getcwd())
config = configparser.ConfigParser()
config.read('./config/config.ini')


file_names = [
    config["file"]["file_keyboards"],
    config["file"]["file_mouses"],
    config["file"]["file_headsets"]
]

session = HTMLSession()

for count, url in enumerate(urls):
    r = session.get(url)
    render_sleep = config['main']['render_sleep']
    r.html.render(sleep=2)
    sheet = fetch(r)
    print(f"checking for changes in {file_names[count]}")
    update(file_names[count], sheet)

