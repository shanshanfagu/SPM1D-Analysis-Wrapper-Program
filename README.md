# SPM1D Desktop Analyzer

A desktop application for One-Dimensional Statistical Parametric Mapping (SPM1D) analysis. No programming skills required!

## Features

- 📁 **Data Import**: Supports CSV/XLSX formats with automatic folder structure recognition for indicators and groups
- 📈 **Normality Test**: Implements D'Agostino-Pearson K² test from spm1d
- 🔬 **Multiple Analyses**: Supports t-tests, ANOVA, regression analysis, etc.
- 🌐 **Bilingual Interface**: Supports English and Simplified Chinese switching
- 📊 **Visualization**: Mean curves, SPM statistical curves, normality test plots, post-hoc test plots
- 💾 **Export**: One-click export to complete Excel reports
- 🚀 **Standalone Executable**: EXE version available, no Python installation required

## Quick Start

### Option 1: Run EXE Directly (No Python required, ~645MB)

1. Download `SPM1D Analyzer.exe`
2. Double-click to run

### Option 2: Run from Source (Lightweight, ~150KB)

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
Data Import → Normality Test → Parameters → Run Analysis → Post-hoc Test → View Charts → Export Data
```

### Data Import

Supports Excel (.xlsx) and CSV formats:
- Single file: Contains data for all groups
- Multiple files: Organized by folders/worksheets

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

## Dependencies

- PyQt5>=5.15.0
- spm1d>=0.4.5
- numpy>=1.20
- pandas>=1.3
- matplotlib>=3.5
- scipy>=1.7
- openpyxl>=3.0

## Tech Stack

Python + PyQt5 + SPM1D + JSON

## License

GPL-3.0 License

## References

- [spm1d Project](https://github.com/0todd0000/spm1d)
- [spm1d Documentation](http://spm1d.org)

