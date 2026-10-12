import matplotlib.pyplot as plt
from kneed import KneeLocator
from sklearn import preprocessing
from sklearn.datasets import make_blobs
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils.extmath import randomized_svd
import random
from scipy.io import mmread
import numpy as np
import matplotlib.pyplot as plt
import time



seed = 1
random.seed(seed)
np.random.seed(seed)

def proj(X):
    return np.transpose(X)@np.linalg.pinv(X@np.transpose(X))@X

def frob_cost_of_proj(A, B):
    U, S, V = np.linalg.svd(B, full_matrices=True)
    Ak = A@proj(V[0:len(S)])
    Atop = A - Ak
    return np.linalg.norm(Atop)**2

class FrequentDirections:
    def __init__(self, sketch_size, dim):
        """
        Parameters:
        - sketch_size (int): the number of rows to retain (l)
        - dim (int): the dimensionality of each row vector (d)
        """
        self.l = sketch_size
        self.d = dim
        self.B = np.zeros((self.l, self.d))  # The sketch matrix

    def append(self, x):
        """
        Append a new row vector x (1D array) to the sketch.
        """
        assert len(x) == self.d
        # Add to first zero row if available
        for i in range(self.l):
            if not np.any(self.B[i]):
                self.B[i] = x
                return
        
        # Full, perform SVD and shrink
        self._shrink_and_replace(x)

    def _shrink_and_replace(self, x):
        """
        When the sketch is full, perform SVD and shrink the matrix.
        """
        # Add new row
        B_augmented = np.vstack([self.B, x])
        U, s, Vt = np.linalg.svd(B_augmented, full_matrices=False)

        # Shrink the singular values
        delta = s[self.l] ** 2
        s_shrunk = np.sqrt(np.maximum(s[:self.l] ** 2 - delta, 0))

        # Rebuild the sketch matrix
        self.B = np.diag(s_shrunk) @ Vt[:self.l]

    def get_sketch(self):
        """
        Return the current sketch matrix.
        """
        return self.B

    def approx_covariance(self):
        """
        Return B^T B, which approximates A^T A.
        """
        return self.B.T @ self.B

def count_rows_not_in_span(U, V, tol=1e-8):
    """
    Count how many rows of U are not in the row span of V.

    Parameters:
        U (array-like): shape (m, d)
        V (array-like): shape (n, d)
        tol (float): numerical tolerance

    Returns:
        int: number of rows in U not in the row span of V
    """

    if(len(V) == 0):
        return len(U)
    
    U = np.atleast_2d(np.asarray(U))
    V = np.atleast_2d(np.asarray(V))

    if V.ndim != 2:
        raise ValueError("V must be a 2D matrix")
    
    count = 0
    for u in U:
        u = np.atleast_2d(u).T  # Column vector shape (d, 1)
        A = V.T  # Shape (d, n)
        b = u    # Shape (d, 1)

        x, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
        reconstructed = A @ x  # Shape (d, 1)
        residual_norm = np.linalg.norm(reconstructed - b)

        if residual_norm > tol:
            count += 1

    return count


# Path to the .mtx file
file_path = 'landmark.mtx'

# Read the matrix (in sparse format)
matrix = mmread(file_path)

# Optionally convert to a dense NumPy array if needed
all_data = matrix.toarray()
#n = 71952
n = 5000
dataset = all_data[:n]
#d = 2704
d = len(dataset[0])
k = 25

#c = 10
c_list = [1.1, 2, 5, 10, 100]
#c_list=[10]
count = -1
factors = []
our_costs = []
true_costs = []
r = 0
old_r = 0
kcurr = 0

i = 0

start_time=time.time()

fd = FrequentDirections(sketch_size=25, dim=d)

V_old = []

recourses = []
recourse = 0
for t in range(n-1):
    next_row = dataset[t]
    fd.append(next_row)
    V_new = fd.get_sketch()
    recourse += count_rows_not_in_span(V_new, V_old)
    recourses.append(recourse)
    V_old = V_new

    if t%100==0:
        print(t)
    
