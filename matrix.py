import numpy as np
import re

def parse_matrix(matrix_str):
    """Parse string like '[[1,2],[3,4]]' to numpy array."""
    try:
        # Clean up the string
        matrix_str = matrix_str.strip()
        # Remove any spaces
        matrix_str = re.sub(r'\s+', '', matrix_str)
        # Evaluate safely
        matrix_list = eval(matrix_str)
        return np.array(matrix_list, dtype=float)
    except:
        raise ValueError("Invalid matrix format. Use [[1,2],[3,4]]")

def matrix_multiply(A_str, B_str):
    """Multiply two matrices."""
    A = parse_matrix(A_str)
    B = parse_matrix(B_str)
    
    steps = [
        f"📊 Matrix A: {A.tolist()}",
        f"📊 Matrix B: {B.tolist()}",
        f"📐 Dimensions: {A.shape} × {B.shape}"
    ]
    
    if A.shape[1] != B.shape[0]:
        raise ValueError(f"Cannot multiply: A columns ({A.shape[1]}) ≠ B rows ({B.shape[0]})")
    
    result = A @ B
    steps.append(f"✅ Result: {result.tolist()}")
    
    return steps, result

def matrix_inverse(matrix_str):
    """Calculate matrix inverse."""
    A = parse_matrix(matrix_str)
    
    steps = [
        f"📊 Matrix: {A.tolist()}",
        f"📐 Dimensions: {A.shape}"
    ]
    
    if A.shape[0] != A.shape[1]:
        raise ValueError("Only square matrices have inverses")
    
    det = np.linalg.det(A)
    steps.append(f"📌 Determinant: {det:.4f}")
    
    if abs(det) < 1e-10:
        raise ValueError("Matrix is singular (determinant ≈ 0), no inverse exists")
    
    inv = np.linalg.inv(A)
    steps.append(f"✅ Inverse: {inv.tolist()}")
    
    return steps, inv

def matrix_determinant(matrix_str):
    """Calculate matrix determinant."""
    A = parse_matrix(matrix_str)
    
    steps = [
        f"📊 Matrix: {A.tolist()}",
        f"📐 Dimensions: {A.shape}"
    ]
    
    if A.shape[0] != A.shape[1]:
        raise ValueError("Determinant only defined for square matrices")
    
    det = np.linalg.det(A)
    steps.append(f"✅ Determinant: {det:.4f}")
    
    return steps, det

def matrix_transpose(matrix_str):
    """Calculate matrix transpose."""
    A = parse_matrix(matrix_str)
    
    steps = [
        f"📊 Matrix: {A.tolist()}",
        f"📐 Dimensions: {A.shape}"
    ]
    
    result = A.T
    steps.append(f"✅ Transpose: {result.tolist()}")
    
    return steps, result

def matrix_eigenvalues(matrix_str):
    """Calculate matrix eigenvalues."""
    A = parse_matrix(matrix_str)
    
    steps = [
        f"📊 Matrix: {A.tolist()}",
        f"📐 Dimensions: {A.shape}"
    ]
    
    if A.shape[0] != A.shape[1]:
        raise ValueError("Eigenvalues only defined for square matrices")
    
    eigenvalues = np.linalg.eigvals(A)
    steps.append(f"✅ Eigenvalues: {eigenvalues.tolist()}")
    
    return steps, eigenvalues