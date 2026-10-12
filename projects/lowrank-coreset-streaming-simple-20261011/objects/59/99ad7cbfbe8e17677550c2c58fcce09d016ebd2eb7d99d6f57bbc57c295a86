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
ratios = [[],[],[],[],[]]
recourses = [[],[],[],[],[]]
runtimes = [[],[],[],[],[]]
r = 0
old_r = 0
kcurr = 0

i = 0

start_time=time.time()

for c in c_list:
    count = -1
    recourse = 0
    sq_norm_At = 0
    for t in range(n-1):
        At = dataset[0:t+1]
        sq_norm_At += np.linalg.norm(At[t])**2
        kcurr = min(r,k)
    ##    if(r > old_r and r <= k):
    ##        kcurr = min(r, k)
    ##        count = sq_norm_At
    ##        factors = V[0:kcurr] 
        if(sq_norm_At>c*count):
            count = sq_norm_At
            U, S, V = randomized_svd(At, n_components = k, n_iter=7, random_state=None)
            factors = V[0:kcurr]
            r = len(V)
            recourse += k
        #old_r = r
        our_cost = frob_cost_of_proj(At, factors)
        if(our_cost < 10**-15):
            #Probably rounding error
            our_cost = 0
        true_cost = frob_cost_of_proj(At, V[0:kcurr])
        if(true_cost < 10**-15):
            #Probably rounding error
            true_cost=0
        our_costs.append(our_cost)
        true_costs.append(true_cost)
        if true_cost==0:
            ratio = 1
        else:
            ratio=our_cost/true_cost
        ratios[i].append(ratio)
        if t%100==0:
            print(t)
        runtimes[i].append(time.time()-start_time)
        recourses[i].append(recourse)
    i = i+1

######################APPROX FIGURE#########################
plt.figure()
# Generate x-axis values (assuming uniform spacing)
x_values = range(1, len(ratios[0]) + 1)

# Plotting ratios
plt.plot(x_values, ratios[0], linestyle='-', label='c=1.1')
plt.plot(x_values, ratios[1], linestyle='-', label='c=2')
plt.plot(x_values, ratios[2], linestyle='-', label='c=5')
plt.plot(x_values, ratios[3], linestyle='-', label='c=10')
plt.plot(x_values, ratios[4], linestyle='-', label='c=100')

plt.yscale('log')
#plt.xlim(1,50000)

# Adding labels and title for loss
plt.xlabel('Number of rows')
plt.ylabel('Ratio of loss')
plt.title('Accuracy for landmark dataset')

#Add legend
plt.legend()
plt.grid(True)
plt.tight_layout()

######################RUNTIME FIGURE#########################
plt.figure()
x_values = range(1, len(runtimes[0]) + 1)

# Plotting runtime
plt.plot(x_values, runtimes[0], linestyle='-', label='c=1.1')
plt.plot(x_values, runtimes[1], linestyle='-', label='c=2')
plt.plot(x_values, runtimes[2], linestyle='-', label='c=5')
plt.plot(x_values, runtimes[3], linestyle='-', label='c=10')
plt.plot(x_values, runtimes[4], linestyle='-', label='c=100')

# Adding labels and title for runtime
plt.xlabel('Number of rows')
plt.ylabel('Total runtime (s)')
plt.title('Total runtime for landmark dataset')

#Add legend
plt.legend()
plt.grid(True)
plt.tight_layout()

######################RECOURSE FIGURE#########################
plt.figure()
x_values = range(1, len(recourses[0]) + 1)

# Plotting recourse
plt.plot(x_values, recourses[0], linestyle='-', label='c=1.1')
plt.plot(x_values, recourses[1], linestyle='-', label='c=2')
plt.plot(x_values, recourses[2], linestyle='-', label='c=5')
plt.plot(x_values, recourses[3], linestyle='-', label='c=10')
plt.plot(x_values, recourses[4], linestyle='-', label='c=100')

# Adding labels and title for recourse
plt.xlabel('Number of rows')
plt.ylabel('Total recourse')
plt.title('Total recourse for landmark dataset')

#Add legend
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()
