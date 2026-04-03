# SPM1D Analyzer v2.81

An application for One-Dimensional Statistical Parametric Mapping (SPM1D) analysis. For the statistical analysis of continuous curve data. No programming skills required! Supports both Chinese and English!

## Features

- 📁 **Data Import**: Supports CSV/XLSX formats with automatic folder structure recognition for indicators and groups. Detects uneven data and recommends interpolation
- 📊 **Data Preprocessing (Optional)**: Data interpolation and denoising
- 📈 **Normality Test**: Implements D'Agostino-Pearson K² test from spm1d
- 🔬 **Multiple Analyses**: Supports t-tests (one-sample, paired, independent), ANOVA (one-way, one-way repeated measures, two-way, two-way repeated measures, two-way mixed design), and simple regression
- 🌐 **Bilingual Interface**: Supports English and Simplified Chinese switching
- 📊 **Visualization**: Mean curves, SPM statistical curves, normality test plots, post-hoc test plots
- 💾 **Export**: One-click export to complete Excel reports
- 🚀 **Standalone**: Supports Windows (.exe) standalone packaging

## Quick Start

### Option 1: Run Standalone (No Python required)

- **Windows**: Download `SPM1D Analyzer.exe`, Double-click to run

### Option 2: Run from Source (Lightweight)

```bash
# Clone or download this project
git clone https://github.com/shanshanfagu/SPM1D-Analysis-Wrapper-Program

# Install dependencies
pip install -r requirements.txt

# Run the program
python SPM1D.py
```

## Workflow

```
Data Import → Data Preprocessing (Optional) → Normality Test → Parameters → Run Analysis → Post-hoc Test → View Charts → Export Data
```

### Data Import

Supports Excel (.xlsx) and CSV formats:
- Single file: Contains data for all groups
- Multiple files: Organized by folders/worksheets
- Automatically detects uneven data (different sample time point counts)

### Data Preprocessing (Optional)

- Data interpolation (interpolate samples to target number of time points)
- Data denoising (low-pass, high-pass, band-pass filtering)
- Files are renamed after preprocessing to indicate applied operations

### Normality Test

- Automatically performs D'Agostino K² test
- Displays test results for each group
- Option to choose parametric/non-parametric methods

### Parameter Settings

| Analysis Type | Description |
|---------------|-------------|
| One-sample t-test | Compare with standard curve |
| Two-sample t-test | Compare two independent or paired samples |
| One-way ANOVA | Compare multiple groups |
| One-way Repeated Measures ANOVA | Compare multiple conditions with same subjects |
| Two-way ANOVA | Two-factor independent groups analysis |
| Two-way Repeated Measures ANOVA | Two-factor analysis with same subjects across all conditions |
| Two-way Mixed Design ANOVA | One between-subjects factor and one within-subjects factor |
| Simple Regression | Single variable trend analysis |

### Data Export

One-click export to complete Excel report (.xlsx)

| Sheet | Content |
|-------|---------|
| Summary | Analysis parameter summary |
| Main Effect Results | SPM curve values |
| Normality Results | K² curve values |
| Post-hoc Results | Pairwise comparison curves |

## Data Format Requirements

### Excel File Format

| Sample\Time Point | T1 | T2 | T3 | T4 | ... |
|-------------------|-----|-----|-----|-----|-----|
| Subject1 | 1.2 | 1.3 | 1.4 | 1.5 | ... |
| Subject2 | 1.1 | 1.2 | 1.3 | 1.4 | ... |
| Subject3 | 1.3 | 1.4 | 1.5 | 1.6 | ... |

- Each column represents a time point
- Each row represents a sample
- Values must be numeric
- Samples within a file can have different time point counts (uneven data). The software detects this and recommends interpolation
- The software reads data starting from the first column and the second row. The first row can be used for custom column labels

## Dependencies

- PyQt5>=5.15.0
- spm1d>=0.4.3
- numpy>=1.20
- pandas>=1.3
- matplotlib>=3.5
- scipy>=1.7
- openpyxl>=3.0

## Tech Stack

Python + PyQt5 + SPM1D + NumPy + SciPy + Pandas + Matplotlib

## License

GPL-3.0 License

## References

- [spm1d Project](https://github.com/0todd0000/spm1d)
- [spm1d Documentation](http://spm1d.org)


