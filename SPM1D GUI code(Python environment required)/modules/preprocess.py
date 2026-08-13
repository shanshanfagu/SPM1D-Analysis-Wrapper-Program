import numpy as np
from scipy.interpolate import CubicSpline
from scipy.signal import butter, filtfilt


def interpolate_data(data, target_points, method='linear'):
    """Interpolate data from original time points to target number of points.

    Args:
        data: numpy array of shape (samples, time_points)
        target_points: int, desired number of time points after interpolation
        method: str, 'linear' or 'cubic'

    Returns:
        numpy array of shape (samples, target_points)

    Raises:
        ValueError: if data shape or target_points are invalid
    """
    if data.ndim != 2:
        raise ValueError("数据必须为二维数组 (样本数 × 时间点数)")

    n_samples, n_points = data.shape

    if n_points < 2:
        raise ValueError("数据时间点数过少，至少需要2个时间点")

    if target_points < 2:
        raise ValueError("目标时间点数必须 >= 2")

    has_nan = np.isnan(data).any()
    if target_points == n_points and not has_nan:
        return data.copy()

    x_old = np.linspace(0, 1, n_points)
    x_new = np.linspace(0, 1, target_points)

    result = np.zeros((n_samples, target_points))

    for i in range(n_samples):
        row = data[i]
        valid_mask = ~np.isnan(row)
        valid_x = x_old[valid_mask]
        valid_y = row[valid_mask]

        if len(valid_y) < 2:
            raise ValueError(f"样本 {i} 的有效数据点不足（仅有 {len(valid_y)} 个），至少需要 2 个")

        if method == 'linear':
            result[i] = np.interp(x_new, valid_x, valid_y)
        elif method == 'cubic':
            cs = CubicSpline(valid_x, valid_y)
            result[i] = cs(x_new)
        else:
            raise ValueError(f"不支持的插值方法: {method}，可选 'linear' 或 'cubic'")

    return result


def butterworth_filter(data, filter_type, cutoff, fs, order=4):
    """Apply 4th-order Butterworth filter to data.

    Args:
        data: numpy array of shape (samples, time_points)
        filter_type: str, 'lowpass', 'highpass', or 'bandpass'
        cutoff: float or list of two floats (for bandpass)
        fs: float, sampling frequency in Hz
        order: int, filter order (default 4)

    Returns:
        numpy array of shape (samples, time_points)

    Raises:
        ValueError: if parameters are invalid
    """
    if data.ndim != 2:
        raise ValueError("数据必须为二维数组 (样本数 × 时间点数)")

    n_samples, n_points = data.shape

    if n_points < order * 3 + 1:
        raise ValueError(f"数据点数过少，至少需要 {order * 3 + 1} 个点进行 {order} 阶滤波")

    if fs <= 0:
        raise ValueError("采样频率必须大于0")

    nyquist = fs / 2.0

    if filter_type == 'bandpass':
        if isinstance(cutoff, (list, tuple, np.ndarray)) and len(cutoff) == 2:
            low, high = float(cutoff[0]), float(cutoff[1])
        else:
            raise ValueError("filter_bandpass_need_two_freqs")
        if low >= high:
            raise ValueError("filter_bandpass_low_high_error")
        if low <= 0:
            raise ValueError("filter_low_freq_positive_error")
        if high >= nyquist:
            raise ValueError("filter_nyquist_error")
        wn = [low / nyquist, high / nyquist]
        btype = 'bandpass'
    elif filter_type in ('lowpass', 'highpass'):
        if isinstance(cutoff, (list, tuple, np.ndarray)):
            cutoff = float(cutoff[0]) if len(cutoff) > 0 else 0
        cutoff = float(cutoff)
        if cutoff <= 0 or cutoff >= nyquist:
            raise ValueError("filter_cutoff_range_error")
        wn = cutoff / nyquist
        btype = 'low' if filter_type == 'lowpass' else 'high'
    else:
        raise ValueError(f"filter_unsupported_type: {filter_type}")

    b, a = butter(order, wn, btype=btype)

    result = np.zeros_like(data, dtype=float)
    for i in range(n_samples):
        result[i] = filtfilt(b, a, data[i])

    return result
