import numpy as np
from benedict import benedict
from sklearn.metrics import mean_squared_error


def residuals_std(y_true, y_pred):
    return np.std(y_true - y_pred)


def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))


def concordance_correlation_coefficient(y_true, y_pred, force_finite=False):
    """Concordance correlation coefficient, from https://github.com/stylianos-kampakis/supervisedPCA-Python
    The concordance correlation coefficient is a measure of inter-rater agreement.
    It measures the deviation of the relationship between predicted and true values
    from the 45 degree angle.
    Read more: https://en.wikipedia.org/wiki/Concordance_correlation_coefficient
    Original paper: Lawrence, I., and Kuei Lin. "A concordance correlation coefficient to evaluate reproducibility." Biometrics (1989): 255-268.  
    Parameters
    ----------
    y_true : array-like of shape = (n_samples) or (n_samples, n_outputs)
        Ground truth (correct) target values.
    y_pred : array-like of shape = (n_samples) or (n_samples, n_outputs)
        Estimated target values.
    Returns
    -------
    loss : A float in the range [-1,1]. A value of 1 indicates perfect agreement
    between the true and the predicted values.
    Examples
    --------
    >>> from sklearn.metrics import concordance_correlation_coefficient
    >>> y_true = [3, -0.5, 2, 7]
    >>> y_pred = [2.5, 0.0, 2, 8]
    >>> concordance_correlation_coefficient(y_true, y_pred)
    0.97678916827853024
    """
    cor = np.corrcoef(y_true,y_pred)[0][1]
    mean_true = np.mean(y_true)
    mean_pred = np.mean(y_pred)
    var_true = np.var(y_true)
    var_pred = np.var(y_pred)
    sd_true = np.std(y_true)
    sd_pred = np.std(y_pred)
    numerator = 2*cor*sd_true*sd_pred
    denominator = var_true + var_pred + (mean_true-mean_pred)**2
    # Standard formula, that may lead to NaN or -Inf
    output_score = numerator / denominator
    if force_finite and (np.isnan(output_score) or np.isinf(output_score)):
        # Default = Zero Numerator = perfect predictions. Set to 1.0
        # (note: even if denominator is zero, thus avoiding NaN scores)
        # Non-zero Numerator and Non-zero Denominator: use the formula
        if np.all(y_true == y_pred) == True:
            output_score = 1.0
        else:
            output_score = 0.0
    return output_score
    # return numerator/denominator


def compute_scores(y_true, y_pred, metrics_to_use_dict: dict):
    # assert level_scoring_map.get(level, None), "No metrics specified for given level."
    results_dict = dict()
    for metric_name, metric_func in metrics_to_use_dict.items():
        results_dict[metric_name] = metric_func(y_true, y_pred)
    return results_dict


def compute_aggregated_scores(epic_reader, data_dict, metrics_to_use_dict: dict):
    store_data_dict = {"arousal_submission": list(), "valence_submission": list(), "arousal_test": list(), "valence_test": list()}
    for subvid_path_str, subvid_submission_annotations in data_dict.items():
        subvid_test_annotations = epic_reader.get_corresponding_test_data(subvid_path_str)
        store_data_dict['arousal_submission'].append(subvid_submission_annotations['arousal'].to_numpy())
        store_data_dict['valence_submission'].append(subvid_submission_annotations['valence'].to_numpy())
        store_data_dict['arousal_test'].append(subvid_test_annotations['arousal'].to_numpy())
        store_data_dict['valence_test'].append(subvid_test_annotations['valence'].to_numpy())
    store_data_dict['arousal_submission'] = np.concatenate(store_data_dict['arousal_submission'])
    store_data_dict['valence_submission'] = np.concatenate(store_data_dict['valence_submission'])
    store_data_dict['arousal_test'] = np.concatenate(store_data_dict['arousal_test'])
    store_data_dict['valence_test'] = np.concatenate(store_data_dict['valence_test'])
    arousal_scores = compute_scores(store_data_dict['arousal_test'], store_data_dict['arousal_submission'], metrics_to_use_dict)
    valence_scores = compute_scores(store_data_dict['valence_test'], store_data_dict['valence_submission'], metrics_to_use_dict)
    return arousal_scores, valence_scores


def compute_averaged_results(results_benedict: benedict, keypath_separator: str = "."):
    "Compute average score at second to last level (dict key). Assumes last level is arousal/valence."
    tmp_benedict = benedict(keypath_separator=keypath_separator)
    # compute max keypath len and check if level is 'folds' - so later when averaging folds we don't average scenario 1
    for keypath in results_benedict.keypaths():
        # split keypath so we can retrieve info from it
        keypath_split = keypath.split(results_benedict.keypath_separator)
        # if averaging between folds level just save scenario 1 - it has shorter keypaths and is already on scenario level
        # if not a number
        if isinstance(results_benedict[keypath], benedict):
            continue
        # create save keypath removing second to last key
        save_keypath = results_benedict.keypath_separator.join(keypath_split[:-3] + keypath_split[-2:])
        # sum results and their count
        tmp_benedict.setdefault(save_keypath, list())
        tmp_benedict[save_keypath].append(results_benedict[keypath])
    # average stored results
    return_benedict = benedict()
    for flat_keypath, samples in tmp_benedict.flatten("/").items():
        flat_keypath_spl = flat_keypath.split("/")
        keypath = return_benedict.keypath_separator.join(flat_keypath_spl)
        if keypath[-4:] == "-std":
            continue
        elif keypath[-5:] == "-mean":
            return_benedict[keypath] = np.mean(samples)
            return_benedict[f"{keypath[:-5]}-std"] = np.std(samples)
            continue
        return_benedict[f"{keypath}-mean"] = np.mean(samples)
        return_benedict[f"{keypath}-std"] = np.std(samples)
    # return benedict with results
    return return_benedict