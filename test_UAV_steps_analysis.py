import pytest
import pandas as pd
import numpy as np
from UAV_steps_analysis import get_idxs_of_low_variance, merge_intervals, get_selected_statistics
from unittest.mock import patch

@pytest.fixture
def sample_data():
    np.random.seed(0)
    data = {
        'index': pd.date_range(start='1/1/2022', periods=100, freq='D'),
        'col': np.concatenate([np.ones(10), np.random.normal(0, 1, 80), np.ones(10)]),
        'stats_col': np.random.normal(0, 1, 100)
    }
    df = pd.DataFrame(data)
    df.set_index('index', inplace=True)
    return df

def test_get_idxs_of_low_variance(sample_data):
    df = sample_data
    window_size = 5
    var_ths = 0.05

    starts, ends = get_idxs_of_low_variance(df, 'col', window_size, var_ths)
    assert all(isinstance(arr, np.ndarray) for arr in [starts, ends])
    assert len(starts) > 0 and len(ends) > 0
    assert all(0 <= start < len(df) for start in starts)
    assert all(0 <= end < len(df) for end in ends)

    starts, ends = get_idxs_of_low_variance(df, 'col', window_size, var_ths=0.0001)
    assert len(starts) == 2 and len(ends) == 2
    assert starts[0] == 0 and ends[0] == 9
    assert 90 <= starts[1] <= 96 and ends[1] == 99

def test_merge_intervals(sample_data):
    df = sample_data

    intervals = merge_intervals(df, 'col', var_ths=0.05, step_size=3)
    assert isinstance(intervals, list) and len(intervals) > 0
    assert all(isinstance(interval, list) and len(interval) == 2 for interval in intervals)

    intervals = merge_intervals(df, 'col', var_ths=0.0001, step_size=3)
    assert len(intervals) == 2
    assert intervals[0][0] <= 6 <= intervals[0][1]
    assert intervals[0][1] == 9
    assert 90 <= intervals[1][0] <= 96
    assert intervals[1][1] == 99

@patch('UAV_steps_analysis.plot_and_select_intervals', return_value=[[10, 20], [30, 40]])
@patch('tkinter.messagebox.askyesno', return_value=True)
def test_get_selected_statistics(mock_askyesno, mock_plot_and_select_intervals, sample_data):
    df = sample_data

    x_means, x_stds, y_means, selections = get_selected_statistics(df, 'col', var_ths=0.05, step_size=3, stats_col='stats_col')
    assert all(isinstance(arr, np.ndarray) for arr in [x_means, x_stds, y_means])
    assert all(len(arr) > 0 for arr in [x_means, x_stds, y_means])
    assert isinstance(selections, list)
    assert all(isinstance(sel, list) and len(sel) == 2 for sel in selections)

    mock_plot_and_select_intervals.return_value = []
    x_means, x_stds, y_means, selections = get_selected_statistics(df, 'col', var_ths=0.05, step_size=3, stats_col='stats_col')
    assert len(selections) == 0
    assert all(len(arr) == 0 for arr in [x_means, x_stds, y_means])
