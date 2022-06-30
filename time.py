from time import localtime, strftime



def get_time_str(format: str = "%Y-%m-%d~%H.%M.%S") -> str:
	s = strftime(format, localtime())
	return s
