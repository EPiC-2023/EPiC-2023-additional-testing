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
        self.download_urls_dict = self._prepare_download_urls()
        self.downloaded_files = list()

    def _parse_config(self) -> tuple[Path]:
        raise Exception("You should implement this method")
    
    def _prepare_download_urls(self) -> dict[str: str]:
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
            urls.setdefault(keypath.replace(".", "/"), url)
        # return list of urls
        return urls

    def _extract_zip_files(self, output_path) -> None:
        # TODO check if output path is a file and treat it accordingly
        # maybe add output_path to config
        # iterate over .zip files
        for zip_path in output_path.glob("**/*.zip"):
            # get relative path
            rel_path = zip_path.relative_to(output_path)
            # extract to download dir
            unzip_path = self.data_download_dir / rel_path.parent / rel_path.stem
            self._uzip(zip_path, unzip_path)
            self._fix_path(zip_path)

    def _uzip(zip_path, unzip_path) -> None:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # make unzip path (remove .zip extension)
            # extract .zip file
            zip_ref.extractall(unzip_path)
            # print message
            print(f"Extracted {zip_path} to {unzip_path}")

    def _fix_path(path) -> None:
        pass

    def _clean_tmp_dir(self, rm_dir=False) -> None:
        # if rm_dir == True, remove tmp dir and exit
        if rm_dir:
            self._remove_from_drive(self.tmp_download_dir)
            return None
        # iterate over content of tmp directory
        for path_to_remove in self.tmp_download_dir.iterdir():
            # skip .gitkeep file
            if path_to_remove.name == ".gitkeep":
                continue
            # remove file
            self._remove_from_drive(path_to_remove)

    def _remove_from_drive(path_to_remove) -> None:
        try:
            shutil.rmtree(path_to_remove)
            # print message
            print(f"Removed {path_to_remove}")
        except OSError as e:
            # print error message
            print(f"Error: {e.filename} - {e.strerror}.")

    def download(self, extract_archives=True, clean_tmp=True, rm_tmp=False) -> None:
        for path, url in self.download_urls_dict.items():
            # prepare output directory
            output_dir = self.tmp_download_dir / Path(path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            # download data from gdrive
            if "file" in url:
                # get file id for file download - download by url does not always work
                # I avoid fuzzy flag, but it could be another solution
                file_id = url.split("/")[-1]
                # make output path for a file
                # directory works only for "download_folder" function
                output_path = str(output_dir) + ".zip"
                gdown.download(id=file_id, output=output_path, quiet=False, use_cookies=False)
            output_path = str(output_dir)
            gdown.download_folder(url, output=output_path, quiet=False, use_cookies=False)
            if extract_archives:
                self._extract_zip_files(output_path)
            if clean_tmp:
                self._remove_from_drive(output_path)
        if clean_tmp:
            self._clean_tmp_dir(rm_tmp)
