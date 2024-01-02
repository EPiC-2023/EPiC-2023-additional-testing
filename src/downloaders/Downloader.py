from benedict import benedict
from pathlib import Path
import gdown
import re
import shutil
import zipfile


DOWNLOAD_KEYPATH_RE = re.compile(r".+\.url")


class Downloader:
    def __init__(self, config: benedict) -> None:
        self.config = config
        self.data_download_dir, self.tmp_download_dir, self.data_skip_download = self._parse_config()
        self.download_urls_dict = self._prepare_download_paths()
        self.download_list = list()

    # def _parse_config(self) -> tuple[Path]:
    #     raise Exception("You should implement this method")
    
    def _parse_config(self) -> tuple[Path]:
        data_download_dir = Path(self.config["download_settings", "download_dir"])
        tmp_download_dir = data_download_dir / "tmp"
        data_skip_download = self.config["download_settings", "skip_download"]
        return data_download_dir, tmp_download_dir, data_skip_download
    
    def _prepare_download_paths(self) -> dict[str: str]:
        # prepare collection to store urls
        urls = dict()
        # iterate over self.config
        for keypath in self.config.keypaths():
            # skip if not url keypath
            if not DOWNLOAD_KEYPATH_RE.match(keypath):
                continue
            # skip if in skip list
            elif keypath.replace(".url", "") in self.data_skip_download:
                continue
            # get url for current download (keypath) and store it
            url = self.config[keypath]
            # make store path based on download url
            # relative_store_path = self._make_store_path(keypath, url)
            relative_store_path = keypath.replace(".url", "").replace(".", "/")
            urls.setdefault(relative_store_path, url)
        # return list of urls
        return urls

    def download(self, extract_archives=True, clean_tmp=True) -> None:
        for rel_path, url in self.download_urls_dict.items():
            # prepare output directory
            output_dir = self.tmp_download_dir / rel_path
            # download data from gdrive
            if "file" in url:
                output_path = Path(str(output_dir) + ".zip")
                self._download_file(url, output_path)
                if extract_archives:
                    self._extract_file(output_path)
                if clean_tmp:
                    self.remove_from_drive(output_path)
            else:
                self._download_folder(url, output_dir)
                if extract_archives:
                    self._extract_from_folder(output_dir)
                if clean_tmp:
                    self.remove_from_drive(output_dir)
            # due to large size of data extract on the go and remove right after
            # if extract_archives:
            #     self._extract_zip_files(output_dir)
        if clean_tmp:
            self._clean_tmp_dir()

    def _download_file(self, url, output_path) -> None:
        # prepare output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # get file id for file download - download by url does not always work
        # I avoid fuzzy flag, but it could be another solution
        file_id = url.split("/")[-1]
        # make output path for a file
        # passing directory works only for "download_folder" function
        output_path = str(output_path)
        gdown.download(id=file_id, output=output_path, quiet=False, use_cookies=False)
        self.download_list.append(output_path)

    def _download_folder(self, url, output_dir) -> None:
        # prepare output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(output_dir)
        gdown.download_folder(url, output=output_path, quiet=False, use_cookies=False)
        self.download_list.append(output_path)

    def _extract_file(self, zip_path) -> None:
        rel_path = zip_path.relative_to(self.tmp_download_dir)
        unzip_path = self.data_download_dir / rel_path.parent
        self.uzip(zip_path, unzip_path)
    
    def _extract_from_folder(self, download_path) -> None:
        # iterate over .zip files
        for zip_path in download_path.glob("**/*.zip"):
            # get relative path
            rel_path = zip_path.relative_to(self.tmp_download_dir).parent
            # extract to download dir
            unzip_path = self.data_download_dir / rel_path
            self.uzip(zip_path, unzip_path)

    @staticmethod
    def uzip(zip_path, unzip_path) -> None:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # make unzip path (remove .zip extension)
            # extract .zip file
            zip_ref.extractall(unzip_path)
            # print message
            print(f"Extracted {zip_path} to {unzip_path}")

    def _clean_tmp_dir(self) -> None:
        # iterate over content of tmp directory
        for path_to_remove in self.tmp_download_dir.iterdir():
            # skip .gitkeep file
            if path_to_remove.name == ".gitkeep":
                continue
            # remove file
            self.remove_from_drive(path_to_remove)

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
