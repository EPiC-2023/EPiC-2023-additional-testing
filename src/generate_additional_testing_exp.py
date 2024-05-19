import numpy as np
import pandas as pd
from pathlib import Path
from shutil import copy, make_archive
from tqdm import tqdm


"""
This code was used to generate data for simulated random physiology experiments.
"""

root_path = Path(__file__).parent.parent
cut_data_to_3_digits = False
zip_data = False
extract_noise_test = True
seed = 42
rng = np.random.default_rng(seed=seed)
competition_data_path = root_path / Path("data/competition/competition_data")
noise_data_path = root_path / Path("data/additional_testing/noise_data")
noise_test_path = root_path / Path("data/additional_testing/noise_test")


if __name__ == "__main__":
    print("Generating noise data")
    for original_data_path in tqdm(sorted(competition_data_path.glob("**/*.csv"))):
        # make target paths
        relative_path = original_data_path.relative_to(competition_data_path)
        noise_data_target_path = noise_data_path / relative_path
        # make dirs if they do not exist
        noise_data_target_path.parent.mkdir(parents=True, exist_ok=True)
        if "physiology" in str(original_data_path):
            # read data file to get a placeholder
            test_data = pd.read_csv(original_data_path)
            # get columns
            cols = test_data.columns.drop("time")
            # generate noise and zero-value flat lines for every physio signal
            noise = rng.normal(loc=0.0, scale=1.0, size=(len(test_data), len(cols)))
            # make and save data
            # replace original data with generated one
            test_data.loc[:, cols] = noise
            # save replaced data
            if cut_data_to_3_digits:
                test_data.to_csv(noise_data_target_path, index=False, float_format='%.3f')
            else:
                test_data.to_csv(noise_data_target_path, index=False)
        else:
            copy(original_data_path, noise_data_target_path)
    # Assert newly generated physiology
    print("Examining simulated random physiology data")
    for file_path in tqdm(noise_data_path.glob("**/physiology/*.csv")):
        data = pd.read_csv(file_path)
        assert all(abs(data.drop(columns=["time"]).mean()) < 0.02), "Wrong mean"
        assert all(abs(data.drop(columns=["time"]).std() - 1.) < 0.02), "Wrong std"
    # assert that annotations did not change
    print("Examining annotations")
    for original_data_path in tqdm(sorted(competition_data_path.glob("**/annotations/*.csv"))):
        # make target paths
        relative_path = original_data_path.relative_to(competition_data_path)
        noise_target_path = noise_data_path / relative_path
        original_annot = pd.read_csv(original_data_path)
        noise_annot = pd.read_csv(noise_target_path)
        assert(all(noise_annot == original_annot)), "Simulated random physiology annotations do not match original ones"
    print("Extracting simulated random physiology test")
    for file_path in tqdm(noise_data_path.glob("**/test/**/*.csv")):
        relative_path = file_path.relative_to(noise_data_path)
        noise_target_path = noise_test_path / relative_path
        noise_target_path.parent.mkdir(parents=True, exist_ok=True)
        copy(file_path, noise_target_path)
    # zip files
    if zip_data:
        print("Compressing data")
        for scenario_dir in tqdm(noise_data_path.iterdir()):
            make_archive(scenario_dir, 'zip', scenario_dir)
            print("Zipped", scenario_dir.stem)
