from requests_html import HTMLSession
import csv
import os


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
        print("something is new!")
        return False
    print("no changes found")
    return True

def exportData(sheet, fileName):
    with open(fileName, "w", newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerows(sheet)

urls = [
    #'https://reshop.lt/collections/klaviaturos',
    #'https://reshop.lt/collections/pelytes',
    'https://reshop.lt/collections/ausines?limit=100'
]

file_names = [
    #'data_keyboards.csv',
    #'data_mouses.csv',
    'data_headsets.csv'
]


session = HTMLSession()
sheet = None

for url in urls:
    r = session.get(url)
    r.html.render(sleep=1)
    sheet = fetch(r)


for file_name in file_names:
    if os.path.isfile(file_name):
        with open(file_name, "r", encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            oldSheet = []
            for line in reader:
                oldSheet.append(line)
            if not isIdentical(oldSheet, sheet):
                list_difference = [item for item in sheet if item not in oldSheet]
                #set_difference = set(sheet) - set(oldSheet)
                #list_difference = list(set_difference)
                if list_difference:
                    print(list_difference[0]) # what's new only, not what's removed tho.
                else:
                    print("something has been removed I guess?")
                #exportData(sheet)
    else:
        exportData(sheet, "data3.csv")