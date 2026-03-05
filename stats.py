import numpy as np
from scipy import stats
import re

def parse_numbers(text):
    """Parse comma or space-separated numbers."""
    text = re.sub(r'[,\s]+', ' ', text)
    numbers = [float(x) for x in text.split()]
    return np.array(numbers)

def basic_stats(numbers_text):
    """Calculate basic statistics."""
    data = parse_numbers(numbers_text)
    
    steps = [
        f"📊 Data: {data.tolist()}",
        f"📊 N = {len(data)} values"
    ]
    
    mean = np.mean(data)
    median = np.median(data)
    std = np.std(data, ddof=1) if len(data) > 1 else 0
    variance = np.var(data, ddof=1) if len(data) > 1 else 0
    min_val = np.min(data)
    max_val = np.max(data)
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    
    steps.extend([
        f"📌 Mean: {mean:.4f}",
        f"📌 Median: {median:.4f}",
        f"📌 Standard deviation: {std:.4f}",
        f"📌 Variance: {variance:.4f}",
        f"📌 Min: {min_val:.4f}",
        f"📌 Max: {max_val:.4f}",
        f"📌 Q1: {q1:.4f}",
        f"📌 Q3: {q3:.4f}",
        f"📌 IQR: {q3 - q1:.4f}"
    ])
    
    return steps, (mean, median, std, variance, min_val, max_val)

def linear_regression(x_text, y_text):
    """Perform linear regression."""
    x = parse_numbers(x_text)
    y = parse_numbers(y_text)
    
    if len(x) != len(y):
        raise ValueError("X and Y must have same length")
    
    steps = [
        f"📊 X: {x.tolist()}",
        f"📊 Y: {y.tolist()}",
        f"📊 N = {len(x)} points"
    ]
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    steps.extend([
        f"📌 Slope: {slope:.4f}",
        f"📌 Intercept: {intercept:.4f}",
        f"📌 R²: {r_value**2:.4f}",
        f"📌 Correlation: {r_value:.4f}",
        f"📌 P-value: {p_value:.4f}",
        f"📌 Standard error: {std_err:.4f}",
        f"✅ Equation: y = {slope:.4f}x + {intercept:.4f}"
    ])
    
    return steps, (slope, intercept, r_value**2)

def t_test_onesample(data_text, popmean=0):
    """One-sample t-test."""
    data = parse_numbers(data_text)
    
    t_stat, p_value = stats.ttest_1samp(data, popmean)
    
    steps = [
        f"📊 Data: {data.tolist()}",
        f"📊 Population mean: {popmean}",
        f"📌 t-statistic: {t_stat:.4f}",
        f"📌 p-value: {p_value:.4f}"
    ]
    
    if p_value < 0.05:
        steps.append("✅ Result: Reject null hypothesis (p < 0.05)")
    else:
        steps.append("✅ Result: Fail to reject null hypothesis (p ≥ 0.05)")
    
    return steps, (t_stat, p_value)

def correlation(x_text, y_text, method='pearson'):
    """Calculate correlation between two variables."""
    x = parse_numbers(x_text)
    y = parse_numbers(y_text)
    
    if method == 'pearson':
        corr, p_value = stats.pearsonr(x, y)
        method_name = "Pearson"
    elif method == 'spearman':
        corr, p_value = stats.spearmanr(x, y)
        method_name = "Spearman"
    else:
        raise ValueError("Method must be 'pearson' or 'spearman'")
    
    steps = [
        f"📊 X: {x.tolist()}",
        f"📊 Y: {y.tolist()}",
        f"📌 {method_name} correlation: {corr:.4f}",
        f"📌 p-value: {p_value:.4f}"
    ]
    
    return steps, (corr, p_value)