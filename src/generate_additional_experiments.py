import numpy as np
import pandas as pd
from pathlib import Path
from shutil import copy, make_archive


"""
This code was used to generate data for additional experiments.
Flat data experiments were not used, so feel free to comment-out code for them.
"""

file_path = Path(__file__)
root_path = file_path.parent.parent
cut_noise_to_3_digits = False
seed = 42
rng = np.random.default_rng(seed=seed)
competition_data_path = root_path / Path("data/competition/competition_data")
noise_data_path = root_path / Path("test_data/post_competition/noise_data")
flat_data_path = root_path / Path("test_data/post_competition/flat_data")

if __name__ == "__main__":
    for original_data_path in sorted(competition_data_path.glob("**/*.csv")):
        # make target paths
        relative_path = original_data_path.relative_to(competition_data_path)
        noise_target_path = noise_data_path / relative_path
        flat_target_path = flat_data_path / relative_path
        # make dirs if they do not exist
        noise_target_path.parent.mkdir(parents=True, exist_ok=True)
        flat_target_path.parent.mkdir(parents=True, exist_ok=True)
        if "physiology" in str(original_data_path):
            # read data file to get a placeholder
            test_data = pd.read_csv(original_data_path)
            # get columns
            cols = test_data.columns.drop("time")
            # generate noise and zero-value flat lines for every physio signal
            noise = rng.normal(loc=0.0, scale=1.0, size=(len(test_data), len(cols)))
            flat_line = np.zeros((len(test_data), len(cols)))
            # make and save data
            for target_path, data in ((noise_target_path, noise), (flat_target_path, flat_line)):
                # replace original data with generated one
                test_data.loc[:, cols] = data
                # save replaced data
                if cut_noise_to_3_digits:
                    test_data.to_csv(target_path, index=False, float_format='%.3f')
                else:
                    test_data.to_csv(target_path, index=False)
        else:
            # make target paths
            copy(original_data_path, noise_target_path)
            copy(original_data_path, flat_target_path)
    # Assert newly generated physiology
    print("Examine noise data")
    for file_path in noise_data_path.glob("**/physiology/*.csv"):
        data = pd.read_csv(file_path)
        assert all(abs(data.drop(columns=["time"]).mean()) < 0.02), "Wrong mean"
        assert all(abs(data.drop(columns=["time"]).std() - 1.) < 0.02), "Wrong std"
    print("Examine flat data")
    for file_path in flat_data_path.glob("**/physiology/*.csv"):
        data = pd.read_csv(file_path)
        assert all(data.drop(columns=["time"]) == 0), "Wrong flat data"
    # assert that annotations did not change
    for original_data_path in sorted(competition_data_path.glob("**/annotations/*.csv")):
        # make target paths
        relative_path = original_data_path.relative_to(competition_data_path)
        noise_target_path = noise_data_path / relative_path
        flat_target_path = flat_data_path / relative_path
        original_annot = pd.read_csv(original_data_path)
        noise_annot = pd.read_csv(noise_target_path)
        flat_annot = pd.read_csv(flat_target_path)
        assert(all(noise_annot == original_annot)), "Bad noise annot"
        assert(all(flat_annot == original_annot)), "Bad flat annot"
    # zip files
    for data_type_path in [noise_data_path, flat_data_path]:
        print("Compressing", data_type_path.stem)
        for scenario_dir in data_type_path.iterdir():
            make_archive(scenario_dir, 'zip', scenario_dir)
            print("Zipped", scenario_dir.stem)

