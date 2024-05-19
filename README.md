# EPiC 2023 additional testing repository

## 1. Repository preparation
To run the code you need python (tested on python 3.11) and libraries from the requirements.txt file.

We recommend using a conda environment with Python >= 3.11 (you can also use standard python, it's just that we tested it using conda).

You can get conda (we recommend miniconda) from [anaconda project website](https://docs.conda.io/en/latest/miniconda.html)

To create the conda environment named `epic` and activate it, run the following code. Omit this step if you don't need a separate environment.
```
conda create -n epic python=3.11 pip
conda activate epic
```

To run the code you need libraries that do not come preinstalled. To install them run:

```
pip install -r requirements.txt
```

## 2. Downloading data
To download data:
1. If you want to skip any url from `config/download_records.jsonl`, put its `get_url` in `skip_urls` list in `src/download_data.py`.
2. Run `src/download_data.py` by executing the following command:

```
python -m src.download_data
```

Downloading predictions and scores is fast, downloading competition and additional_testing data takes much longer (although it depends on the speed of your internet connection). 
