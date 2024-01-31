# EPiC 2023 analysis repository

## 1. Repository preparation
To run the code you need python (tested on python 3.11) and libraries from the requirements.txt file.

We recommend using a conda environment with Python >= 3.11 (you can also use standard python, it's just that we tested it using conda).

You can get conda (we recommend miniconda) from [anaconda project website](https://docs.conda.io/en/latest/miniconda.html)

To create the conda environment named `epic_scoring` and activate it, run the following code. Omit this step if you don't need a separate environment.
```
conda create -n epic_scoring python=3.11 pip
conda activate epic_scoring
```

To run the code you need libraries that do not come preinstalled. To install them run:

```
pip install -r requirements.txt
```

## 2. Downloading data
To download data:
1. Select data that you want to download in `config/download_config.toml`. If you want to skip some files, put their names in `skip_download` lists. Settings for data, predictions and scores downloads are to be set separately.
2. Run `src/download_data.py` by invoking the following command:

```
python -m src.download_data
```

Downloading predictions and scores is fast, downloading competition and post_competition data takes a long time. 
