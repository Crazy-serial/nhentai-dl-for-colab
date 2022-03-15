import os
import pathlib
import time
import img2pdf
import requests
from bs4 import BeautifulSoup
import glob
from PIL import Image


def make_folder(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


class Scrape_Tool:
    def __init__(self):
        self.requests = requests
        self.bs4 = BeautifulSoup
        self.artwork_urls = []
        self.pil_img = Image
        self.os = os
        self.artwork_pages = 0
        self.artwork_img_urls = []
        self.artwork_title = ""
        self.artwork_titles = []
        self.artwork_parody = []
        self.artwork_character = []
        self.artwork_tag = []
        self.artwork_language = ""

    def artwork_collector(self, page, keyword="", dump=False):
        if page == 0:
            return self.artwork_urls
        if keyword == "":
            url = "https://nhentai.to/language/japanese"
        else:
            url = "https://nhentai.to/search?q=" + keyword.replace(" ", "+")

        if "?" in url:
            page_url = f"{url}&page={page}"
        else:
            page_url = f"{url}/?page={page}"
        print(f"requesting: {page_url}")

        response = self.requests.get(page_url)
        html = self.bs4(response.text, "lxml")
        try:
            self.artwork_pages = int(html.find("a", class_="last").get("href").split("=")[-1])
        except:
            self.artwork_pages = 1

        covers = html.find_all("a", class_="cover")
        for cover in covers:
            art_work_url = "https://nhentai.to" + cover.get("href")
            self.artwork_urls.append(art_work_url)
            if dump:
                with open("artwork_urls.txt", "a") as f:
                    f.write(art_work_url + "\n")
                f.close()
        return self.artwork_urls

    def scrape_artwork_info(self, url, optimization_artwork_name=True):
        response = self.requests.get(url)
        html = self.bs4(response.text, "lxml", from_encoding="utf-8")

        # title
        h1_list = html.find_all("h1")
        for title in h1_list:
            if title != "Recommended Hentai Porn Games":
                self.artwork_title = title.get_text()

        if optimization_artwork_name:
            symbols = [r"/", r"\a".replace("a", "")]
            for symbol in symbols:
                self.artwork_title = self.artwork_title.replace(symbol, ".")
        self.artwork_titles.append(self.artwork_title)
        print(self.artwork_title, ":", url)

        lan = "/language/"
        parody = "/parody/"
        char = "/character/"
        tag = "/tag/"
        self.artwork_language = ""
        self.artwork_parody = []
        self.artwork_character = []
        self.artwork_tag = []
        a_tag = html.find_all("a")
        # language, parody, character
        for a in a_tag:
            a_href = a.get("href")
            if a_href != None:
                if lan in a_href:
                    self.artwork_language = a_href.replace(lan, "").replace("/", "")
                elif parody in a_href:
                    self.artwork_parody.append(a_href.replace(parody, "").replace("/", ""))
                elif char in a_href:
                    self.artwork_character.append(a_href.replace(char, "").replace("/", ""))
                elif tag in a_href:
                    self.artwork_tag.append(a_href.replace(tag, "").replace("/", ""))
                else:
                    pass

        # img_list
        url_elements = html.find_all("img")
        self.artwork_img_urls = []
        for img in url_elements:
            if "data-src" in str(img):
                small_img_urls = img.get("data-src")
                self.artwork_img_urls.append(small_img_urls.replace("t.jpg", ".jpg").replace("t.png", ".png"))

    def download_image_by_sequence(self, urls, output_path, overwrite=False):
        artwork_id = urls[0].split("/")[-2]
        self.output_path_with_id = f"{output_path}/{artwork_id}"
        if not os.path.exists(self.output_path_with_id):
            os.makedirs(self.output_path_with_id)
        pro_size = len(urls) - 1
        for i in range(len(urls)):
            img_format = urls[i][-4:]
            if len(str(i)) == 1:
                number = "00" + str(i + 1)
            elif len(str(i)) == 2:
                number = "0" + str(i + 1)
            else:
                number = str(i + 1)
            save_name = f"{self.output_path_with_id}/{artwork_id}_{number}{img_format}"
            while True:
                if not overwrite:
                    if self.os.path.isfile(save_name):
                        break
                img_content = requests.get(urls[i]).content
                with open(save_name, mode="wb") as f:
                    f.write(img_content)
                f.close()
                try:
                    self.pil_img.open(save_name)
                except:
                    self.os.remove(save_name)
                    print("FileSaveError_Retry ", end="")
                else:
                    break
            pro_bar = ("=" * i) + (" " * (pro_size - i))
            print("\r[{0}] {1}/{2}".format(pro_bar, i, pro_size), end="")
        print(" ")


class Tool:
    def __init__(self):
        self.glob = glob
        self.img2pdf = img2pdf
        self.os = os

    def image_to_pdf(self, image_directory, save_pdf, overwrite=False):
        if not overwrite:
            if self.os.path.isfile(save_pdf):
                print("File already exists")
                return None
        print(f"{image_directory} ==> {save_pdf}")
        output_dir = save_pdf.replace(save_pdf.split("/")[-1], "")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        image_list = sorted(self.glob.glob(image_directory + "/*"))
        try:
            pdf = self.img2pdf.convert(image_list)
        except:
            print(f"ConvertError: {save_pdf}")
        with open(save_pdf, "wb") as f:
            f.write(pdf)
        f.close()

    #def tag_separater(self):        
    #with open('test.txt', 'a') as f:
    #    f.write('deep insider\n')


if __name__ == "__main__":
    scr = Scrape_Tool(requests, BeautifulSoup, Image, os)
    img = Tool(glob, img2pdf, os)

    for i in range(1, 5):
        urls = scr.artwork_collector(i)

    reject_tag_list = ["males-only", "shotacon", "yaoi", "futanari", "dickgirl on male", "males only"]

    for url in urls:
        scr.scrape_artwork_info(url)
        if scr.artwork_language == "japanese":
            tag_switch = True
            for reject_tag in reject_tag_list:
                if reject_tag in scr.artwork_tag:
                    tag_switch = False
                    break
            print(tag_switch)
            if tag_switch:
                if len(scr.artwork_img_urls) < 50:
                    scr.download_image_by_sequence(scr.artwork_img_urls, "img")
                    # img.image_to_pdf(scr.output_path_with_id, f"./pdf/{scr.artwork_title}.pdf")
                    img.image_to_pdf(scr.output_path_with_id, f"/googledrive/Othercomputers/AMD/python_code/nhentai/pdf/{scr.artwork_title}.pdf")
                    print()
