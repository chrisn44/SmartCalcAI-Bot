import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import io
from calculator import safe_parse

def plot_function(func_str, xmin, xmax, var='x', ymin=None, ymax=None):
    """Generate 2D plot and return BytesIO object."""
    var_sym = sp.Symbol(var)
    expr = safe_parse(func_str)
    f = sp.lambdify(var_sym, expr, modules='numpy')
    
    x_vals = np.linspace(xmin, xmax, 1000)
    y_vals = f(x_vals)
    
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, 'b-', linewidth=2, label=f'${sp.latex(expr)}$')
    plt.grid(True, alpha=0.3)
    plt.xlabel(var)
    plt.ylabel(f'f({var})')
    plt.title(f'Plot of ${sp.latex(expr)}$')
    plt.axhline(y=0, color='k', linewidth=0.5)
    plt.axvline(x=0, color='k', linewidth=0.5)
    
    if ymin is not None and ymax is not None:
        plt.ylim(ymin, ymax)
    else:
        y_vals_clean = y_vals[np.isfinite(y_vals)]
        if len(y_vals_clean) > 0:
            y_min = np.percentile(y_vals_clean, 1)
            y_max = np.percentile(y_vals_clean, 99)
            plt.ylim(y_min, y_max)
    
    plt.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

def plot_multiple(funcs_str, xmin, xmax, var='x'):
    """Plot multiple functions on same graph."""
    var_sym = sp.Symbol(var)
    func_list = [f.strip() for f in funcs_str.split(',')]
    
    plt.figure(figsize=(10, 6))
    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k']
    
    x_vals = np.linspace(xmin, xmax, 1000)
    
    for i, func_str in enumerate(func_list):
        expr = safe_parse(func_str)
        f = sp.lambdify(var_sym, expr, modules='numpy')
        y_vals = f(x_vals)
        plt.plot(x_vals, y_vals, color=colors[i % len(colors)], 
                linewidth=2, label=f'${sp.latex(expr)}$')
    
    plt.grid(True, alpha=0.3)
    plt.xlabel(var)
    plt.ylabel(f'f({var})')
    plt.title('Multiple Functions Plot')
    plt.axhline(y=0, color='k', linewidth=0.5)
    plt.axvline(x=0, color='k', linewidth=0.5)
    plt.legend()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

def plot3d_function(func_str, xmin, xmax, ymin, ymax, var_x='x', var_y='y'):
    """Generate 3D surface plot (premium feature)."""
    from mpl_toolkits.mplot3d import Axes3D
    
    x_sym = sp.Symbol(var_x)
    y_sym = sp.Symbol(var_y)
    expr = safe_parse(func_str)
    f = sp.lambdify((x_sym, y_sym), expr, modules='numpy')
    
    x_vals = np.linspace(xmin, xmax, 50)
    y_vals = np.linspace(ymin, ymax, 50)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = f(X, Y)
    
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8, linewidth=0, antialiased=True)
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
    
    ax.set_xlabel(var_x)
    ax.set_ylabel(var_y)
    ax.set_zlabel('f')
    ax.set_title(f'3D Plot of ${sp.latex(expr)}$')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf