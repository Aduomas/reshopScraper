from requests_html import HTMLSession
import csv
import os
import configparser
import io
import sys
import logging
import argparse

# make a logger.

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] - %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("./log/main.log", encoding="utf-8-sig"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def fetch(r):
    items = r.html.xpath('//div[@id="gf-products"]/div')

    sheet = [["Name", "Price", "Link"]]

    for item in items:
        raw_name = item.xpath("//a/text()")
        name = ""
        for s in raw_name:
            if s == "\n":
                continue
            name += s

        link = "https://reshop.lt" + item.xpath("//a/@href")[0]

        if price := item.xpath(
            '//span[@class="spf-product-card__saleprice money"]/text()'
        ):
            price = price[0]
        elif price := item.xpath(
            '//span[@class="spf-product-card__price money"]/text()'
        ):
            price = price[0]

        sheet.append([name, price, link])
    return sheet


def export_data(sheet, fileName):
    with open(fileName, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerows(sheet)


def update(file_name, sheet, to_save):
    if os.path.isfile(file_name):
        with open(file_name, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            oldSheet = []
            for line in reader:
                oldSheet.append(line)
            # slow algorithm
            if oldSheet != sheet:
                list_difference = [item for item in sheet if item not in oldSheet]
                if list_difference:
                    logging.info("added: \n" + str(list_difference[0]))
                list_difference = [item for item in oldSheet if item not in sheet]
                if list_difference:
                    logging.info("removed: \n" + str(list_difference[0]))
            else:
                logging.info("no changes found!")
    else:
        export_data(sheet, file_name)
        logging.info(f"exported data into {file_name}")
    if to_save and oldSheet != sheet:
        export_data(sheet, file_name)
        logging.info(f"exported data into {file_name}")


urls = [
    "https://reshop.lt/collections/klaviaturos",
    "https://reshop.lt/collections/pelytes",
    "https://reshop.lt/collections/ausines?limit=100",
]
config = configparser.ConfigParser()
config.read("./config/config.ini")


file_names = [
    config["file"]["file_keyboards"],
    config["file"]["file_mouses"],
    config["file"]["file_headsets"],
]

logging.info("initializing the session")
session = HTMLSession()


# command line arguments
parser = argparse.ArgumentParser(description="Description")
parser.add_argument("-s", "--Save", help="Save updates into the file")
args = parser.parse_args()
to_save = False
if args.Save:
    to_save = True


for count, url in enumerate(urls):
    logging.info(f"sending a request to {url}")

    r = session.get(url)
    render_sleep = int(config["main"]["render_sleep"])
    r.html.render(sleep=render_sleep)
    sheet = fetch(r)
    logging.info(f"checking for changes in {file_names[count]}")

    update(file_names[count], sheet, to_save)
