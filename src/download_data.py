from benedict import benedict
from pathlib import Path
from .downloaders import Downloader


BASE_DIR = Path(__file__).parent.parent


if __name__ == "__main__":
    # load config
    config = benedict.from_toml(BASE_DIR / "config" / "download_config.toml")
    # get config for data download 
    data_setup_config = config["data"]
    # setup data downloader
    data_downloader = Downloader(data_setup_config)
    # download data
    data_downloader.download(extract_archives=True, clean_tmp=True)
    # exit()
    # get config for predictions download 
    predictions_setup_config = config["predictions"]
    # setup predictions downloader
    predictions_downloader = Downloader(predictions_setup_config)
    # download data
    predictions_downloader.download(extract_archives=True, clean_tmp=True)