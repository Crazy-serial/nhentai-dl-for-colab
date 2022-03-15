from gigafile import Uploader, Downloader, Tools

tools = Tools()
up = Uploader(True)
files = tools.select_files("/googledrive/MyDrive/nhentai-dl-for-colab/pdf")
url = up.send_files(files)
print(f"ギガファイル便のurl: {url}")
print("アップロードされたファイルを消去しますか？（アップロードされたファイルを確認してから消去してください）")
if "yes" == input("yes or no>>> "):
    os.rmdir("/googledrive/MyDrive/nhentai-dl-for-colab/pdf")