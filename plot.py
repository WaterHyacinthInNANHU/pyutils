import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm

def reject_outliers(data, m=2, method='mean'):
	if method == 'mean':
		return data[abs(data - np.mean(data)) < m * np.std(data)]
	elif method == 'median':
		d = np.abs(data - np.median(data))
		mdev = np.median(d)
		s = d/mdev if mdev else 0.
		return data[s<m]
	else:
		raise ValueError('unknown method: "{}"'.format(method))
	

def stage(X, Y, ahead=False):
	assert(len(X) == len(Y))
	inter_x, inter_y = [], []
	for idx in range(len(X)-1):
		if not ahead:
			inter_x.append(X[idx+1])
			inter_y.append(Y[idx])
		else:
			inter_x.append(X[idx])
			inter_y.append(Y[idx+1])
	# cross the two list
	staged_x = [item for pair in zip(X, inter_x) for item in pair]
	staged_y = [item for pair in zip(Y, inter_y) for item in pair]
	return staged_x, staged_y


def plot_multicolor_line(x: np.array, y: np.array, mask: np.array, cmap: str or plt.cmap = 'Paired', linewidth: int = None):
	"""plot multi-color line
	ref: https://matplotlib.org/2.0.2/examples/pylab_examples/multicolored_line.html
	
	Args:
		x (np.array): x
		y (np.array): y
		mask (np.array): The color mask of data points, having same size as x and y. Recommend to fill it with int or bool. 
		cmap (str or plt.cmap, optional): The cmap to use. Defaults to 'Paired'.
		linewidth (int, optional): the width of the line. Defaults to None.
	"""
	assert (x.shape == y.shape and y.shape == mask.shape), 'x, y, mask should have same shape, but {},{},{} was given'.format(x.shape, y.shape, z.shape)

	mask = mask[1:]
	unq, mask = np.unique(mask, return_inverse=True)
	unq = np.arange(len(unq))
	if type(cmap) == str:
		cmap = plt.get_cmap(cmap, len(unq))
	norm = BoundaryNorm(list(unq-0.5) + [unq[-1]+0.5], cmap.N)
	points = np.array([x, y]).T.reshape(-1, 1, 2)
	segments = np.concatenate([points[:-1], points[1:]], axis=1)
	lc = LineCollection(segments, cmap=cmap, norm=norm)
	lc.set_array(mask)
	if linewidth:
		lc.set_linewidth(linewidth)
	plt.gca().add_collection(lc)
	

