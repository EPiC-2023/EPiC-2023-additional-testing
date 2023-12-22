from pathlib import Path
from benedict import benedict
from ._Downloader import Downloader


class DataDownloader(Downloader):
    def __init__(self, config: benedict) -> None:
        super().__init__(config)

    def _parse_config(self) -> tuple[Path]:
        data_download_dir = Path(self.config["download_settings", "download_dir"])
        tmp_download_dir = data_download_dir / "tmp"
        data_skip_download = self.config["download_settings", "skip_download"]
        return data_download_dir, tmp_download_dir, data_skip_download
