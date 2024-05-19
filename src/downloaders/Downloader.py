from pathlib import Path
import shutil
import zipfile
import requests


class Downloader:
    def __init__(self, root_dir, skip_urls = None, tmp_dir_relative="tmp") -> None:
        self.root_dir = root_dir
        self.tmp_dir = root_dir / tmp_dir_relative
        self.skip_urls = skip_urls or [""]

    def download(self, download_records, extract_archives=False, clean_tmp=False) -> None:
        for download_dict in download_records:
            if download_dict["get_url"] in self.skip_urls:
                print(f"""Skipping {download_dict["get_url"]} ({download_dict["type"]} {download_dict["name"]})""")
                continue
            # prepare output directory
            output_dir = self.tmp_dir / download_dict["type"]
            # download data from gdrive
            download_path = self.download_url(download_dict["get_url"], output_dir, download_dict["name"])
            if extract_archives and download_dict.get("extract_dir"):
                self.unzip(download_path, self.root_dir / download_dict.get("extract_dir"))
            if clean_tmp:
                self.remove_from_drive(download_path)
        if clean_tmp:
            self._clean_tmp_dir()

    def unzip(self, zip_path, unzip_path) -> None:
        print(f"Extracting {zip_path} to {unzip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # make unzip path (remove .zip extension)
            # extract .zip file
            zip_ref.extractall(unzip_path)
            # print message
            print(f"Extracted {zip_path} to {unzip_path}")

    def _clean_tmp_dir(self) -> None:
        # iterate over content of tmp directory
        for path_to_remove in self.tmp_dir.iterdir():
            # skip .gitkeep file
            if path_to_remove.name == ".gitkeep":
                continue
            # remove file
            self.remove_from_drive(path_to_remove)

    @staticmethod
    def download_url(url, root, filename=None):
        # make sure root is path
        root = Path(root)
        # if no filename, extract it from url
        if not filename:
            filename = Path(url).name
        # path to save file
        fpath = root / filename
        # make parent dir 
        fpath.parent.mkdir(parents=True, exist_ok=True)
        # download data
        try:
            print('Downloading ' + url + ' to ' + str(fpath))
            r = requests.get(url, allow_redirects=True)
            with open(fpath, 'wb') as f:
                f.write(r.content)
        except:
            print(f"Could not download {url}")
            return None
        # return path to file if successfully downloaded
        return fpath

    @staticmethod
    def remove_from_drive(path_to_remove) -> None:
        path_to_remove = Path(path_to_remove)
        try:
            if path_to_remove.is_dir():
                shutil.rmtree(path_to_remove)
            else:
                path_to_remove.unlink()
            # print message
            print(f"Removed {path_to_remove}")
        except OSError as e:
            # print error message
            print(f"Error: {e.filename} - {e.strerror}.")
