import time

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
browser = Chrome(options=options)

url = "https://www.nationalgeographic.com/animals/mammals/facts/domestic-cat"

start_time = time.time()
browser.get(url)
print("Done")
end_time = time.time()

print(browser.page_source)

print(end_time - start_time)

