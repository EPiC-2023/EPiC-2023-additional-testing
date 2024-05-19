from pathlib import Path
from benedict import benedict
from sklearn.metrics import r2_score
from src.scoring.EPICReader import EPICReader
from tqdm import tqdm
from functools import partial
from src.scoring.scoring_utils import residuals_std, rmse, concordance_correlation_coefficient, compute_scores, compute_aggregated_scores, compute_averaged_results
import argparse
import re
import ast


"""
An alternative code for scoring.
The main difference to the original code is that this one does not contain safeguards against cheating.
It is also simpler to use and modify than the original code.
Computation logic is the same as in original scoring code, so RMSE values remain the same.
"""


def get_group(path):
    fold_search = re.search(r"fold_\d", str(path))
    return fold_search.group() if fold_search is not None else None


def score_results_dir(team_results_dir):
    team_results_benedict = benedict()
    for scenario_dir in team_results_dir.iterdir():
        scenario = scenario_dir.name
        # file-wise computations
        for subvid_path_str, subvid_submission_annotations in epic_reader.iter_subvid_data(scenario_dir):
            subvid_path = Path(subvid_path_str)
            subvid_test_annotations = epic_reader.get_corresponding_test_data(subvid_path_str)
            fold_num = epic_reader.extract_fold_num(subvid_path_str)
            arousal_submission = subvid_submission_annotations['arousal'].to_numpy()
            valence_submission = subvid_submission_annotations['valence'].to_numpy()
            arousal_test = subvid_test_annotations['arousal'].to_numpy()
            valence_test = subvid_test_annotations['valence'].to_numpy()
            arousal_scores = compute_scores(arousal_test, arousal_submission, level_scoring_map["files"])
            valence_scores = compute_scores(valence_test, valence_submission, level_scoring_map["files"])
            if scenario == "scenario_1":
                team_results_benedict["files_level", scenario, subvid_path.stem, "arousal"] = arousal_scores
                team_results_benedict["files_level", scenario, subvid_path.stem, "valence"] = valence_scores
                continue
            team_results_benedict["files_level", scenario, fold_num, subvid_path.stem, "arousal"] = arousal_scores
            team_results_benedict["files_level", scenario, fold_num, subvid_path.stem, "valence"] = valence_scores
        # subject-wise computations
        for subject_num, subject_data_dict in epic_reader.iter_subjects_data(scenario_dir):
            arousal_scores, valence_scores = compute_aggregated_scores(epic_reader, subject_data_dict, level_scoring_map["subjects"])
            team_results_benedict["subjects_level", scenario, f"sub_{subject_num}", "arousal"] = arousal_scores
            team_results_benedict["subjects_level", scenario, f"sub_{subject_num}", "valence"] = valence_scores
        # video-wise computations
        for video_num, video_data_dict in epic_reader.iter_videos_data(scenario_dir):
            arousal_scores, valence_scores = compute_aggregated_scores(epic_reader, video_data_dict, level_scoring_map["videos"])
            team_results_benedict["videos_level", scenario, f"vid_{video_num}", "arousal"] = arousal_scores
            team_results_benedict["videos_level", scenario, f"vid_{video_num}", "valence"] = valence_scores
        # fold-wise average
        team_results_benedict["folds_level", scenario] = compute_averaged_results(team_results_benedict["files_level", scenario])
        # scenario-wise average
        if scenario == "scenario_1":
            team_results_benedict["scenarios_level", scenario] = team_results_benedict["folds_level", scenario]
        else:
            team_results_benedict["scenarios_level", scenario] = compute_averaged_results(team_results_benedict["folds_level", scenario])
        # compute scenario-wise subjects and videos average
        team_results_benedict["scenarios_level-subjects", scenario] = compute_averaged_results(team_results_benedict['subjects_level', scenario])
        team_results_benedict["scenarios_level-videos", scenario] = compute_averaged_results(team_results_benedict['videos_level', scenario])
    return team_results_benedict


parser = argparse.ArgumentParser(description='Score submissions.')

parser.add_argument(
    "--finite", type=ast.literal_eval, default=True
)
parser.add_argument(
    "--name", type=str, default="", required=True
)

args = vars(parser.parse_args())
root = Path(__file__).parent.parent
test_path = root / Path("data/competition/test_annotations/") # test data
predictions_dir = root / "predictions"
scores_dir = root / "scores"
submissions_path = predictions_dir / args["name"]

assert submissions_path in list(predictions_dir.iterdir()), f"""'{args["name"]}' not found in {predictions_dir}"""

if args["finite"]:
    new_scoring_dir = scores_dir / (args["name"] + "-finite") # scores with forced finite ccc values
else:
    new_scoring_dir = scores_dir / args["name"] # just scores

epic_reader = EPICReader(test_path)

level_scoring_map = {
    'files': {
        'ccc': partial(concordance_correlation_coefficient, force_finite=args["finite"]),
        'r2_score': r2_score,
        'rmse': rmse,
        'residuals_std': residuals_std,
    },
    'subjects': {
        'ccc': partial(concordance_correlation_coefficient, force_finite=args["finite"]),
        'r2_score': r2_score,
        'residuals_std': residuals_std,
        'rmse': rmse,
    },
    'videos': {
        'ccc': partial(concordance_correlation_coefficient, force_finite=args["finite"]),
        'r2_score': r2_score,
        'residuals_std': residuals_std,
        'rmse': rmse,
    },
}

subvid_to_fold = {
    scenario_path.name: {file_path.stem: get_group(file_path) for file_path in scenario_path.glob("**/*.csv")}
    for scenario_path in test_path.iterdir()
    }

folds_subvids = benedict()
for scenario_path in test_path.iterdir():
    folds_subvids.setdefault(scenario_path.name, dict())
    for file_path in scenario_path.glob("**/*.csv"):
        fold = get_group(file_path)
        folds_subvids[scenario_path.name].setdefault(fold, list())
        folds_subvids[scenario_path.name, fold].append(file_path.stem)

for team_dir in tqdm(submissions_path.iterdir()):
    if team_dir.name == "tmp":
        continue
    if team_dir.name == "results":
        team_name = "."
        team_results_dir = team_dir
    else:
        team_name = team_dir.name
        team_results_dir = team_dir / "results"
    team_results_benedict = score_results_dir(team_results_dir)
    # save results
    team_results_benedict.to_json(filepath=new_scoring_dir / team_name / "scores.json")