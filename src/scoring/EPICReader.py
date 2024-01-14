from pathlib import Path
from benedict import benedict
import re
import json
import pandas as pd


class EPICReader:
    def __init__(self, test_dir) -> None:
        self.root_dir_path = Path(__file__).parent.parent.parent
        # self.submissions_dir = Path(submissions_dir)
        # self.scenario = None
        self.test_dir = Path(test_dir)
        self.test_annotations = benedict(keypath_separator=">")
        self.test_paths = benedict(keypath_separator=">")
        self.ids_map_path = self.root_dir_path / "data" / "old_new_ids_map.json"
        self.fold_search_re = re.compile(r"fold\_\d")
        self.scenario_search_re = re.compile(r"scenario\_\d")
        self.relative_path_re = re.compile(r"scenario_.+\.csv")
        self.scenarios_num_folds = {
            "scenario_1": None,
            "scenario_2": 5,
            "scenario_3": 4,
            "scenario_4": 2
        }
        self.OLD_NEW_IDS = None
        self.NEW_OLD_IDS = None
        self.load_data()

    def load_data(self):
        # load ids maps
        self.OLD_NEW_IDS, self.NEW_OLD_IDS = self.load_ids_maps(self.ids_map_path) 
        # make path to read test data
        # scenario_test_dir = self.root_dir_path / f"scenario_{self.scenario}"
        # iterate test data path and save test annotations and file path (for later scoring) 
        for file_path in self.test_dir.glob(pattern=f"**/test/annotations/*.csv"):
            # subvid_str = file_path.stem
            self.test_annotations[str(file_path.relative_to(self.test_dir))] = self.read_annotations_file(file_path)
            # self.test_paths[subvid_str] = file_path.relative_to(self.root_dir_path)

    @staticmethod
    def load_ids_maps(path):
        def _recurrent_dict_swap(ids_dict):
            _, v = next(iter(ids_dict.items()))
            if isinstance(v, int):
                return {str(v): k for k, v in ids_dict.items()}
            return {k: _recurrent_dict_swap(v) for k, v in ids_dict.items()}
        with open(path, "r") as fp:
            old_to_new_ids_map = json.load(fp)
        new_to_old_ids_map = _recurrent_dict_swap(old_to_new_ids_map)
        return benedict(old_to_new_ids_map), benedict(new_to_old_ids_map)
    
    def extract_fold_num(self, file_path):
        if not isinstance(file_path, str):
            file_path = str(file_path)
        fold_search = self.fold_search_re.search(file_path)
        if fold_search is None:
            return None
        return fold_search.group()
    
    def extract_scenario_num(self, file_path):
        if not isinstance(file_path, str):
            file_path = str(file_path)
        scenario_search = self.scenario_search_re.search(file_path)
        if scenario_search is None:
            return None
        return scenario_search.group()
    
    def extract_subject_num(self, file_path):
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        return file_path.stem.split("_")[1]
    
    def extract_video_num(self, file_path):
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        return file_path.stem.split("_")[3]

    def subvid_old_to_new(self, scenario, subject=None, video=None, subvid=None):
        if isinstance(scenario, int):
            scenario = f"scenario_{scenario}"
        assert subject or video or subvid, "Specify at least one argument"
        ret = dict()
        if subject:
            subject = self.OLD_NEW_IDS[scenario]['subjects'][str(subject)]
            ret['subject'] = subject
        if video:
            video = self.OLD_NEW_IDS[scenario]['videos'][str(video)]
            ret['video'] = video
        if subvid:
            _, subject, _, video = subvid.split("_")
            ret["subvid"] = f"sub_{self.OLD_NEW_IDS[scenario]['subjects'][str(subject)]}_vid_{self.OLD_NEW_IDS[scenario]['videos'][str(video)]}"
        return ret
    
    def subvid_new_to_old(self, scenario, subject=None, video=None, subvid=None):
        if isinstance(scenario, int):
            scenario = f"scenario_{scenario}"
        assert subject or video or subvid, "Specify at least one argument"
        ret = dict()
        if subject:
            subject = self.NEW_OLD_IDS[scenario]['subjects'][str(subject)]
            ret['subject'] = subject
        if video:
            video = self.NEW_OLD_IDS[scenario]['videos'][str(video)]
            ret['video'] = video
        if subvid:
            _, subject, _, video = subvid.split("_")
            ret["subvid"] = f"sub_{self.NEW_OLD_IDS[scenario]['subjects'][subject]}_vid_{self.NEW_OLD_IDS[scenario]['videos'][video]}"
        return ret

    def read_annotations_file(self, file_path):
        df = pd.read_csv(file_path)
        if "time" in df.columns:
            df.drop(columns=["time"], inplace=True)
        return df

    def get_subject_data(self, dir_path, subject_num):
        annotations_dict = dict()
        for file_path in dir_path.glob(pattern=f"**/test/annotations/sub_{subject_num}_*.csv"):
            annotations_dict[str(file_path.relative_to(dir_path.parent))] = self.read_annotations_file(file_path)
        return annotations_dict

    def get_video_data(self, dir_path, video_num):
        annotations_dict = dict()
        for file_path in dir_path.glob(pattern=f"**/test/annotations/*vid_{video_num}.csv"):
            annotations_dict[str(file_path.relative_to(dir_path.parent))] = self.read_annotations_file(file_path)
        return annotations_dict

    def get_corresponding_test_data(self, file_path):
        corr_re = self.relative_path_re.search(file_path)
        if corr_re is None:
            return None
        return self.test_annotations[corr_re.group()]
    
    def get_num_folds(self, scenario):
        return self.scenarios_num_folds[scenario]

    def iter_subjects_data(self, dir_path):
        subjects = {self.extract_subject_num(file_path) for file_path in dir_path.glob(pattern=f"**/test/annotations/*.csv")}
        for subject_num in subjects:
            yield (subject_num, self.get_subject_data(dir_path, subject_num))

    def iter_videos_data(self, dir_path):
        videos = {self.extract_video_num(file_path) for file_path in dir_path.glob(pattern=f"**/test/annotations/*.csv")}
        for video_num in videos:
            yield (video_num, self.get_video_data(dir_path, video_num))

    def iter_subvid_data(self, dir_path):
        for file_path in dir_path.glob(pattern=f"**/test/annotations/*.csv"):
            yield (str(file_path.relative_to(dir_path.parent)), self.read_annotations_file(file_path))
