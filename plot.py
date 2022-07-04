import numpy as np

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
