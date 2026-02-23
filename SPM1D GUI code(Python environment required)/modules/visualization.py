import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import spm1d
from utils.config import COLORS

def setup_plot_style():
    plt.style.use('seaborn-v0_8-whitegrid')
    matplotlib.rcParams['font.family'] = 'sans-serif'
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial', 'DejaVu Sans', 'Microsoft YaHei']
    matplotlib.rcParams['axes.edgecolor'] = COLORS['secondary']
    matplotlib.rcParams['axes.linewidth'] = 0.8
    matplotlib.rcParams['grid.alpha'] = 0.3
    matplotlib.rcParams['axes.unicode_minus'] = False

def plot_mean_sd(data_dict, ax=None, save_path=None):
    setup_plot_style()
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = COLORS['line_colors']
    x = np.arange(data_dict[list(data_dict.keys())[0]].shape[1])
    
    for i, (group_name, data) in enumerate(data_dict.items()):
        mean = np.mean(data, axis=0)
        sd = np.std(data, axis=0, ddof=1)
        
        color = colors[i % len(colors)]
        ax.plot(x, mean, color=color, linewidth=2, label=group_name)
        ax.fill_between(x, mean - sd, mean + sd, color=color, alpha=0.2)
    
    ax.set_xlabel('Time Point', fontsize=12)
    ax.set_ylabel('Value', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path
    
    return ax

def plot_spm_result(spm_result, inference_result, ax=None, save_path=None, test_type='ttest', two_tailed=True):
    setup_plot_style()

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(spm_result.z))
    z = spm_result.z
    zstar = abs(inference_result.zstar)
    
    ax.plot(x, z, color=COLORS['primary'], linewidth=2)

    if two_tailed:
        ax.axhline(y=zstar, color='red', linestyle='--', linewidth=1.5)
        ax.axhline(y=-zstar, color='red', linestyle='--', linewidth=1.5)
        ax.fill_between(x, zstar, z, where=(z > zstar), color='red', alpha=0.3)
        ax.fill_between(x, -zstar, z, where=(z < -zstar), color='red', alpha=0.3)
        ax.text(x[-1] * 0.95, zstar + 0.3, f'+z* = {zstar:.4f}',
                ha='center', va='bottom', fontsize=9, color='red')
        ax.text(x[-1] * 0.95, -zstar - 0.3, f'-z* = {-zstar:.4f}',
                ha='center', va='top', fontsize=9, color='red')
    else:
        ax.axhline(y=zstar, color='red', linestyle='--', linewidth=1.5)
        ax.fill_between(x, zstar, z, where=(z > zstar), color='red', alpha=0.3)
        ax.text(x[-1] * 0.95, zstar + 0.3, f'+z* = {zstar:.4f}',
                ha='center', va='bottom', fontsize=9, color='red')

    ax.set_xlabel('Time Point', fontsize=12)
    
    if test_type in ['ttest', 'ttest2', 'ttest_paired', 'regress']:
        ax.set_ylabel('SPM{t}', fontsize=12)
    elif test_type == 'anova1':
        ax.set_ylabel('SPM{F}', fontsize=12)
    else:
        ax.set_ylabel('SPM{z}', fontsize=12)
        
    ax.grid(True, alpha=0.3)

    if hasattr(inference_result, 'p') and inference_result.p is not None:
        p_values = inference_result.p
        if isinstance(p_values, (list, np.ndarray)):
            if hasattr(inference_result, 'clusters') and inference_result.clusters is not None:
                for i, (p, cluster) in enumerate(zip(p_values, inference_result.clusters)):
                    p_str = "<0.001" if p < 0.001 else f"{p:.4f}"
                    if hasattr(cluster, 'endpoints'):
                        start, end = cluster.endpoints
                        start_idx = int(start)
                        end_idx = int(end)
                        start_idx = max(0, min(start_idx, len(z) - 1))
                        end_idx = max(0, min(end_idx, len(z) - 1))
                        region_z = z[start_idx:end_idx+1]
                        if len(region_z) > 0:
                            max_idx = np.argmax(region_z)
                            max_x = start_idx + max_idx
                            max_z = region_z[max_idx]
                            ax.text(max_x, max_z + 0.5, f'p = {p_str}',
                                    ha='center', va='bottom', fontsize=9, color='black')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path

    return ax

def create_combined_figure(data_dict, spm_result, inference_result, save_path=None, test_type='ttest'):
    setup_plot_style()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    plot_mean_sd(data_dict, ax=ax1)
    
    plot_spm_result(spm_result, inference_result, ax=ax2, test_type=test_type)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path
    
    return fig

def export_figure(fig, filepath, format='png'):
    valid_formats = ['png', 'pdf', 'svg']
    if format not in valid_formats:
        format = 'png'

    filepath = f"{filepath}.{format}" if not filepath.endswith(f'.{format}') else filepath
    fig.savefig(filepath, dpi=300, bbox_inches='tight', format=format)
    return filepath

def plot_posthoc_result(spm_result, inference_result, ax=None, save_path=None, title=None):
    setup_plot_style()

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(spm_result.z))
    z = spm_result.z
    zstar = abs(inference_result.zstar)

    ax.plot(x, z, color=COLORS['primary'], linewidth=2)

    ax.axhline(y=zstar, color='red', linestyle='--', linewidth=1.5)
    ax.axhline(y=-zstar, color='red', linestyle='--', linewidth=1.5)
    ax.fill_between(x, zstar, z, where=(z > zstar), color='red', alpha=0.3)
    ax.fill_between(x, -zstar, z, where=(z < -zstar), color='red', alpha=0.3)
    ax.text(x[-1] * 0.95, zstar + 0.3, f'+z* = {zstar:.4f}',
            ha='center', va='bottom', fontsize=9, color='red')
    ax.text(x[-1] * 0.95, -zstar - 0.3, f'-z* = {-zstar:.4f}',
            ha='center', va='top', fontsize=9, color='red')

    ax.set_xlabel('Time Point', fontsize=12)
    ax.set_ylabel('SPM{z}', fontsize=12)
    ax.grid(True, alpha=0.3)

    if title:
        ax.set_title(title, fontsize=12)

    if hasattr(inference_result, 'p') and inference_result.p is not None:
        p_values = inference_result.p
        if isinstance(p_values, (list, np.ndarray)):
            if hasattr(inference_result, 'clusters') and inference_result.clusters is not None:
                for i, (p, cluster) in enumerate(zip(p_values, inference_result.clusters)):
                    p_str = "<0.001" if p < 0.001 else f"{p:.4f}"
                    if hasattr(cluster, 'endpoints'):
                        start, end = cluster.endpoints
                        start_idx = int(start)
                        end_idx = int(end)
                        start_idx = max(0, min(start_idx, len(z) - 1))
                        end_idx = max(0, min(end_idx, len(z) - 1))
                        region_z = z[start_idx:end_idx+1]
                        if len(region_z) > 0:
                            max_idx = np.argmax(region_z)
                            max_x = start_idx + max_idx
                            max_z = region_z[max_idx]
                            ax.text(max_x, max_z + 0.5, f'p = {p_str}',
                                    ha='center', va='bottom', fontsize=9, color='black')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path

    return ax

def plot_k2_result(spm_result, inference_result, ax=None, save_path=None, group_name=None):
    setup_plot_style()

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(spm_result.z))
    k2_values = spm_result.z
    zstar = inference_result.zstar

    ax.plot(x, k2_values, color='black', linewidth=2)
    ax.axhline(y=zstar, color='red', linestyle='--', linewidth=1.5)
    ax.fill_between(x, zstar, k2_values, where=(k2_values > zstar), color='red', alpha=0.3)

    ax.set_xlabel('Time Point', fontsize=12)
    ax.set_ylabel('K2 Statistic', fontsize=12)
    ax.grid(True, alpha=0.3)

    if group_name:
        ax.set_title(f"D'Agostino K2 Normality Test: {group_name}", fontsize=12)

    mean_k2 = np.mean(k2_values)
    p_value = inference_result.p
    if isinstance(p_value, (list, np.ndarray)):
        p_value = np.mean(p_value)
    p_str = "<0.001" if p_value < 0.001 else f"{p_value:.4f}"

    stats_text = f'Mean K2: {mean_k2:.4f}\np-value: {p_str}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax.text(x[-1] * 0.95, zstar + 0.3, f'z* = {zstar:.4f}',
            ha='center', va='bottom', fontsize=9, color='red')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight', format=save_path.split('.')[-1] if '.' in save_path else 'png')
        plt.close()
        return save_path

    return ax
