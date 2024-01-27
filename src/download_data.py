from benedict import benedict
from pathlib import Path
from .downloaders import Downloader


BASE_DIR = Path(__file__).parent.parent


if __name__ == "__main__":
    # load config
    config = benedict.from_toml(BASE_DIR / "config" / "download_config.toml")
    for download_type in ["data", "predictions", "scores"]:
        # get config for data download 
        data_setup_config = config[download_type]
        # setup data downloader
        data_downloader = Downloader(data_setup_config)
        # print message
        print(f"Downloading {download_type}")
        # download data
        data_downloader.download(extract_archives=True, clean_tmp=True)
