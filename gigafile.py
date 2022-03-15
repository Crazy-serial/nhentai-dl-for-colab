import glob
import os
import shutil
import time

from selenium import webdriver
from selenium.webdriver.common.alert import Alert


class Chrome:
    def __init__(self, download_path=""):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-startup-window")
        self.options.add_argument(f"--app=file://{os.getcwd()}")
        self.abs_download_path = os.path.abspath(download_path)
        if not os.path.isdir(self.abs_download_path):
            os.mkdir(self.abs_download_path)
        prefs = {"download.default_directory": self.abs_download_path}
        self.options.add_experimental_option("prefs", prefs)

    def driver_options(self, *args):
        for arg in args:
            self.options.add_argument(arg)

    def driver(self, colab=False):
        if colab:
            self.options.add_argument("--headless")
            self.driver = webdriver.Chrome("chromedriver", options=self.options)
        elif not colab:
            from webdriver_manager.chrome import ChromeDriverManager

            self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=self.options)
        self.driver.set_window_size(1000, 1000)
        return self.driver


###########################################################################################


class Uploader:
    def __init__(self, colab=False):
        self.driver = Chrome().driver(colab)
        self.alert = Alert
        self.uploaded_file_urls = {}
        self.uploaded_zip_url = ""

    def send_files(self, directory, date=7, zip_file_name="", zip_password=""):
        self.driver.get("https://gigafile.nu/")
        self.driver.execute_script("arguments[0].scrollIntoView();", self.driver.find_element_by_id("lifetime_meter_box"))
        date_and_element_dict = {}
        date_number = 1
        while True:
            try:
                date_element = self.driver.find_element_by_xpath(f'//ul[@id="lifetime_divisions"]/li[{date_number}]')
            except:
                break
            else:
                date_and_element_dict[date_element.get_attribute("data-lifetime-val")] = date_number
                date_number += 1
        if date != 7:
            self.driver.find_element_by_xpath(f'//*[@id="lifetime_divisions"]/li[{date_and_element_dict[str(date)]}]').click()
        status = None
        already_found = False
        file_element = '//div[@id="file_{}"]'
        if type(directory) is str:
            send_file = directory
            uploaded_number = 0
            print("str")
            if not os.path.isfile(send_file):
                raise FileNotFoundError("Please enter the File path")
        elif type(directory) is list:
            if directory == []:
                raise FileNotFoundError("Please enter the File path")
            for dir in directory:
                if not os.path.isfile(dir):
                    raise FileNotFoundError("Please enter the File path")
            uploaded_number = len(directory) - 1
            send_file = " \n ".join(directory)
        else:
            raise FileNotFoundError("Enter as a list or string")
        input_button = self.driver.find_element_by_xpath('//*[@id="upload_panel_button"]/input')
        input_button.send_keys(send_file)
        while True:
            try:
                status = self.driver.find_element_by_xpath(file_element.format(uploaded_number) + '//span[@class="status"]').text
            except:
                pass
            if status != None:
                if not already_found:
                    if "%" in status:
                        already_found = True
                elif already_found:
                    if not "%" in status:
                        break
        for i in range(uploaded_number + 1):
            file_url = self.driver.find_element_by_xpath(file_element.format(i) + '//a[@class="file_info_url link_btn"]').get_attribute("href")
            self.uploaded_file_urls[directory[i]] = file_url
        button = self.driver.find_element_by_xpath('//div[@id="matomete_btn"]')
        self.driver.execute_script("arguments[0].scrollIntoView();", button)
        if zip_file_name != "":
            zip_file_name = self.driver.find_element_by_xpath('//input[@id="zip_file_name"]')
            zip_file_name.clear()
            zip_file_name.send_keys(zip_file_name)
        if zip_password != "":
            zip_dlkey = self.driver.find_element_by_xpath('//input[@id="zip_dlkey"]')
            zip_dlkey.clear()
            zip_dlkey.send_keys(zip_password)
        button.click()
        while True:
            try:
                Alert(self.driver).accept()
            except:
                pass
            else:
                break
        self.uploaded_zip_url = self.driver.find_element_by_xpath('//a[@id="matomete_link_btn"]').get_attribute("href")
        self.driver.refresh()
        while True:
            try:
                Alert(self.driver).accept()
            except:
                pass
            else:
                break
        return self.uploaded_zip_url


class Downloader:
    def __init__(self, download_path, colab=False):
        self.download_path = download_path
        self.chrome = Chrome(download_path)
        self.driver = self.chrome.driver(colab)

    def download(self, url, separate=False):
        self.driver.get(url)
        if not separate:
            self.driver.execute_script(f'download_zip("{url.split("/")[-1]}", false, false)')
        elif separate:
            separate_file_count = 0
            while True:
                try:
                    separate_file_button = self.driver.find_element_by_xpath(
                        f'//div[@id="matomete_file[{separate_file_count}]"]/div[@class="matomete_dl_ctrl"]/button[@class="download_panel_btn_dl gfbtn"]'
                    )
                except:
                    break
                else:
                    self.driver.execute_script("arguments[0].scrollIntoView();", separate_file_button)
                    separate_file_button.click()
                separate_file_count += 1
        while True:
            cr_list = glob.glob(self.download_path + "/*.crdownload")
            if cr_list == []:
                break


class Tools:
    def __init__(self, temp_dir="./giga_temp"):
        self.file_directories = ""
        self.tmp_zip_directories = []
        self.temp = temp_dir

    def select_files(self, *directories):
        self.file_directories = []
        for dir in directories:
            abspath = os.path.abspath(dir)
            if os.path.isfile(abspath):
                self.file_directories.append(abspath)
            elif os.path.isdir(abspath):
                in_dir_files = glob.glob(abspath + "/*")
                for in_dir_file in in_dir_files:
                    if os.path.isfile(in_dir_file):
                        self.file_directories.append(in_dir_file)
                    elif os.path.isdir(in_dir_file):
                        if not os.path.isdir(self.temp):
                            os.mkdir(self.temp)
                        zip = os.path.abspath(f"{self.temp}/" + in_dir_file.split("/")[-1])
                        shutil.make_archive(zip, "zip", root_dir=in_dir_file)
                        zip += ".zip"
                        if os.path.isfile(zip):
                            self.file_directories.append(zip)
                            self.tmp_zip_directories.append(zip)
        return self.file_directories

    def delete_tmp(self):
        if os.path.isdir(self.temp):
            shutil.rmtree(self.temp)
