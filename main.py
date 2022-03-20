from nhentai_class_new import Scrape_Tool, Tool
import glob, shutil, os
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

page = int(config['scraper']['request_page'])
language = config['scraper']['language']
require_keyword = config['scraper']['require_keyword']
pdf_path = config['files']['pdf_path']
img_cache_path = config['files']['img_cache_path']
downloaded_url_list = config['txt']['downloaded_url_list']
reject_tag_list = config['txt']['reject_tag_list']
reject_name_list = config['txt']['reject_name_list']

scr = Scrape_Tool()
img = Tool()

def file_writer(txt_path, content):
    with open(txt_path, 'a') as f:
        f.write(f'{content}\n')

def file_reader(txt_path):
    with open(txt_path, 'a') as f:
        f.write(f'')
    with open(txt_path) as r:
        content = r.readlines()
    return sorted(list(set(content)))

def file_check(path, artwork_name):
    check = os.path.isfile(path+f"{artwork_name}.pdf")
    if check:
        return False
    if not check:
        return True


if require_keyword == "True":
    print("検索ワードを入力してください")
    print("入力されなかった場合、日本語最新の作品からを取得します")
    search = input(">>> ")
elif require_keyword == "False":
    search = ""
else:
    exit()

print("何ページ分取得しますか？")
page = int(input(">>> "))
print(f"{page}ページ分の作品を取得します")
reject_tag_list = file_reader(reject_tag_list)
reject_name_list = file_reader(reject_name_list)
for i in range(1, page+1):
    if search != "":
      urls = scr.artwork_collector(i, search)
    else:
      urls = scr.artwork_collector(i)

downloaded_url = file_reader(downloaded_url_list)
for i in range(len(urls)):
    if not urls[i] in downloaded_url:
        scr.scrape_artwork_info(urls[i])
        name_switch = True
        for name in reject_name_list:
          if name in scr.artwork_title:
            name_switch = False
        if name_switch:
          if not os.path.isfile(pdf_path + f"{scr.artwork_title}.pdf"):
              if scr.artwork_language == language:
                  tag_switch = True
                  for reject_tag in reject_tag_list:
                      if reject_tag in scr.artwork_tag:
                          tag_switch = False
                          break
                  if tag_switch:
                      scr.download_image_by_sequence(scr.artwork_img_urls, img_cache_path)
                      img.image_to_pdf(scr.output_path_with_id, pdf_path + f"{scr.artwork_title}.pdf")
                      print()
    file_writer(downloaded_url_list, urls[i])


