import os

def get_module_path(module, full=True):
	"""get the absolute path of dictionary/path of the current module

	Args:
		module (_type_): eg: __file__
		full (bool): whether to return full path
	"""
	if full:
		p = os.path.abspath(module)
	else:
		p = os.path.dirname(os.path.abspath(module))
	return p

def get_cwd():
	p = os.path.abspath(os.getcwd())
	return p

def mkdirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def list_all(dir_path, condition=lambda x: True):
	"""list all file that satisfy the condition

	Args:
		dir_path (_type_): target folder path
		condition (_type_): function or lambda

	Returns:
		_type_: a list of file path
	"""
	# os.path.splitext(f)[1] == '.pth'
	res = [os.path.join(dp, f) for dp, dn, filenames in os.walk(dir_path) for f in filenames if condition(f)]
	return res

def list_dir(dir_path, condition=lambda x: True):
	"""list items under given dir that satisfy the condition

	Args:
		dir_path (_type_): target folder path
		condition (_type_): filter, a function or lambda

	Returns:
		_type_: a list of file path
	"""
	res = [os.path.join(dir_path, f) for f in os.listdir(dir_path)] # list all
	res = [item for item in res if condition(item)] # filter
	return res

def file_name(path, extension = True):
	base=os.path.basename(path)
	if not extension:
		base = os.path.splitext(base)[0]
	return base