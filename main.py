# 下載由 Python http-server 架設的完整檔案目錄

from tqdm.auto import tqdm  # pip install tqdm
from urllib.request import urlretrieve, urlopen  # pip install urllib3
from urllib.parse import unquote
from urllib.error import URLError, HTTPError
from queue import Queue
import os
import re

url = "http://10.17.15.250:12345/"
output_path = "./AIS3教材/"


def fetch_url_content(target_url):
    try:
        with urlopen(target_url) as response:
            return response.read().decode('utf-8')
    except (URLError, HTTPError) as e:
        print(f"Error fetching {target_url}: {e}")
        return None


def process_download_queue():
    downloadQueue = Queue()
    initial_content = fetch_url_content(url)
    if initial_content:
        for link in re.findall(r'<a href="([^"]+)">', initial_content):
            downloadQueue.put(link)

    while not downloadQueue.empty():
        current = downloadQueue.get()
        os.makedirs(os.path.dirname(os.path.join(output_path, unquote(current))), exist_ok=True)

        if current.endswith('/'):
            directory_content = fetch_url_content(url + current)
            if directory_content:
                for link in re.findall(r'<a href="([^"]+)">', directory_content):
                    downloadQueue.put(current + link)
        else:
            download_file(current)


def download_file(relative_path):
    full_path = os.path.join(output_path, unquote(relative_path))
    if not os.path.exists(full_path):
        with tqdm(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=unquote(relative_path)) as t:
            urlretrieve(url + relative_path, full_path, reporthook=progress_hook(t))
    else:
        print("Already Exist, Skipped!")


def progress_hook(t):
    last_b = [0]

    def update_to(b=1, bsize=1, tsize=None):
        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b

    return update_to


if __name__ == "__main__":
    process_download_queue()