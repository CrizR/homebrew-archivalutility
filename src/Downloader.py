import json
import os
import threading

import requests

from src.Utils import Utils


class Downloader(object):
    MAX_CONCURRENT_DOWNLOADS = 8

    def __init__(self, src, dest, api_key):
        self.src = src
        self.dest = dest
        self.api_key = api_key
        self.sema = threading.Semaphore(value=self.MAX_CONCURRENT_DOWNLOADS)
        self.total_downloaded = 0

    def write_to_file(self, filename, content):
        """ simple helper method to write files onto the local filesystem """

        if not os.path.exists(self.dest):
            os.makedirs(self.dest)

        with open(os.path.join(self.dest, filename), 'wb') as f:
            f.write(content)

    def download(self, url, total):
        """ execute the get request and write the file """
        self.sema.acquire()
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Dropbox-API-Arg": json.dumps({"path": url[0]})
        }
        resp = requests.post("https://content.dropboxapi.com/2/files/download", headers=headers)

        self.write_to_file(url[1], resp.content)
        self.total_downloaded += 1
        Utils.print_progress_bar(self.total_downloaded, total, prefix="Downloading Files")
        self.sema.release()

    def get_urls(self):
        """ filter the response for all available items via href """
        urls = []
        headers = {
            "Authorization": "Bearer " + self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "path": self.src,
            "recursive": False,
            "include_media_info": False,
            "include_deleted": False,
            "include_has_explicit_shared_members": True,
            "include_mounted_folders": True,
            "include_non_downloadable_files": False
        }
        resp = requests.post("https://api.dropboxapi.com/2/files/list_folder", headers=headers, data=json.dumps(
            payload))

        for entry in resp.json()['entries']:
            if entry['path_lower'] != self.src.lower():
                if ".zip" not in entry['name']:
                    urls.append((entry['path_lower'], entry['name']))

        return sorted(urls)

    def run(self):
        urls = self.get_urls()
        threads = list()
        for idx, url in enumerate(urls):
            thread = threading.Thread(target=self.download, args=(url, len(urls)))
            threads.append(thread)
            thread.start()

    def get_files(self):
        urls = self.get_urls()
        with open("files.csv", "w+") as f:
            for i, url in enumerate(urls):
                Utils.print_progress_bar(i, len(urls), prefix="Retrieving File Names")
                f.writelines(url[0] + "\n")
