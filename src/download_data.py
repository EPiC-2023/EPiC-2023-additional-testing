from pathlib import Path
from .downloaders import Downloader
import json


def read_jsonl(fpath):
    records = None
    with open(fpath, "r") as fp:
        records = list(map(json.loads, fp.readlines()))
    return records


root_dir = Path(__file__).parent.parent
download_records_path = root_dir / "config" / "download_records.jsonl"
skip_urls = []


if __name__ == "__main__":
    # load records
    download_records = read_jsonl(download_records_path)
    # setup data downloader
    data_downloader = Downloader(root_dir, skip_urls, tmp_dir_relative="tmp")
    # download data
    data_downloader.download(download_records, extract_archives=True, clean_tmp=True)
