from os import system

# commands = ["pip install img2pdf", "pip install bs4", "pip install pillow"]
commands = [
    "pip install selenium",
    "apt-get update",
    "apt install chromium-chromedriver",
    "cp /usr/lib/chromium-browser/chromedriver /usr/bin"
]

for run in commands:
    system(run)
