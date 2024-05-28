# EPiC 2023 additional testing repository

## 1. Repository preparation
To run the code you need python (tested on python 3.11) and libraries from the requirements.txt file.

We recommend using a conda environment with Python >= 3.11 (you can also use standard python, it's just that we tested it using conda).

You can get conda (we recommend miniconda) from [anaconda project website](https://docs.conda.io/en/latest/miniconda.html)

To create the conda environment named `epic-additional-testing` and activate it, run the following code. Omit this step if you don't need a separate environment.
```
conda create -n epic-additional-testing python=3.11 pip
conda activate epic-additional-testing
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

You can also download data manually, either by pasting `get_url` that you want into your browser, or by opening project [releases](https://github.com/Emognition/EPiC-2023-additional-testing/releases).

## 3. Running other code
To run scripts (.py files) you can use the method from step 2, i.e., run `src/<script name>.py` by executing the following command:

```
python -m src.<script name>
```

To run notebooks (.ipynb files) you can open them in an IDE that can open notebook files (e.g., VS Code), or by:
1. Executing `jupyter-notebook` command in the repository (in terminal)
2. Opening resulting URL in your internet browser (should look similar to `http://localhost:8888/tree?token=...`)
3. Opening the file you are interested in and running it

The files that may be interested in:
- `src/generate_additional_testing_exp.py` - code used to generate data for random simulated physiology experiments
- `src/score_predictions.py` - code used to score predictions (RMSE calculation works the same as in [scoring repo](https://github.com/Emognition/EPiC-2023-scoring), but without boilerplate code unnecessary at this stage)
- `src/make_baselines.ipynb` - code used to make baselines (finally only fold-wise baseline was used)
- `src/make_physiology_examples.ipynb` - code used to create examples of corresponding regular and random simulated physiology

## 4. Repository's backup
You can find a backup of all files in the related [OSF project](https://osf.io/r96p8/). Files in the project have the same names as in `name` field of the `config/download_records.jsonl` file, so you can download them manually and extract to the path specified in `extract_dir` field in each record.
