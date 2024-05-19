from pathlib import Path
from benedict import benedict
import pandas as pd
import re
import json


def load_maps(path):
    def recurrent_dict_swap(ids_dict):
        _, v = next(iter(ids_dict.items()))
        if isinstance(v, int):
            return {str(v): k for k, v in ids_dict.items()}
        return {k: recurrent_dict_swap(v) for k, v in ids_dict.items()}
    with open(path, "r") as fp:
        old_to_new_ids_map = json.load(fp)
    new_to_old_ids_map = recurrent_dict_swap(old_to_new_ids_map)
    return benedict(old_to_new_ids_map), benedict(new_to_old_ids_map)


subvid_search_re = re.compile(r"sub\_\d+\_vid\_\d+")
scenario_search_re = re.compile(r"scenario_\d")
root_path = Path(__file__).parent.parent
OLD_TO_NEW_IDS_MAP, NEW_TO_OLD_IDS_MAP = load_maps(root_path / "data" / "original_to_changed_ids_map.json")
with open(root_path / "data" / "original_stimuli_labels.json", "r") as fp:
    VIDEOS_LABELS = json.load(fp)
LABEL_TO_VIDNUM = {vid_dict["label"]: vid_num for vid_num, vid_dict in VIDEOS_LABELS.items()}


def recurrent_subvid_ids_swap(results_dict, new_to_old_ids_map=NEW_TO_OLD_IDS_MAP, prev_keys=''):
    k, v = next(iter(results_dict.items()))
    if isinstance(v, float):
        return results_dict
    if subvid_search_re.search(k):
        ret_dict = dict()
        scenario = scenario_search_re.search(prev_keys).group()
        for sample_num, sample_dict in results_dict.items():
            _, subject_id, _, video_id = subvid_search_re.search(sample_num).group().split('_')
            subject_id, video_id = new_to_old_ids_map[scenario, 'subjects', subject_id], new_to_old_ids_map[scenario, 'videos', video_id]
            ret_dict.setdefault(f"sub_{subject_id}_vid_{video_id}", sample_dict)
        return ret_dict
    return {k: recurrent_subvid_ids_swap(v, new_to_old_ids_map, prev_keys + '/' + k) for k, v in results_dict.items()}


def load_scores_file(scores_path):
    with open(scores_path) as fp:
        scores = json.load(fp)
    scores = recurrent_subvid_ids_swap(scores)
    return scores


def load_scores(scoring_path, team_name_first=False, load_levels_list=['folds_level', 'scenarios_level', 'files_level'], exclude_teams=None, benedict_keypath_sep='>'):
    scoring_path = Path(scoring_path)
    all_scores_benedict = benedict(keypath_separator=benedict_keypath_sep)
    exclude_teams_set = set(exclude_teams) if exclude_teams is not None else set()
    for scores_file_path in scoring_path.glob("**/*.json"):
        scores_dict = load_scores_file(scores_file_path)
        team_name_str = scores_file_path.parent.name
        if team_name_str in exclude_teams_set:
            continue
        for level_str in load_levels_list:
            scores_benedict = benedict(scores_dict[level_str], keypath_separator=benedict_keypath_sep)
            # bottleneck here (flatten method)
            if team_name_first:
                all_scores_benedict[team_name_str, level_str] = scores_benedict.flatten(separator='/')
            else:
                all_scores_benedict[level_str, team_name_str] = scores_benedict.flatten(separator='/')
    return all_scores_benedict
