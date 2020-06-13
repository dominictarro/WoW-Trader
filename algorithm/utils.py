from pathlib import Path
import sys, os, time
from contextlib import contextmanager


class PathError(Exception):
	''''''

class PathFinder:
	def __init__(self, delimiter="/", recursion_depth=7):
		self.delimiter	= delimiter
		self.tpath		= None
		self.found		= False
		self.traversed	= set([])
		self.target		= None
		self.relative	= False
		self.depth_max 	= recursion_depth

	def forward_prop(self, directory, depth):
		try:
			self.traversed.add(directory)
			# Get directory contents
			contents = os.listdir(directory)

			# Check if target is in the directory
			# Target is a relative directory
			if self.relative:
				abs_dir = f"{directory}{self.delimiter}{self.target}"
				# Check if this is a valid directory. If yes, stop all recursion
				if os.path.exists(abs_dir):
					self.tpath = directory
					self.found = True
				else:
					# If no, list the subdirectories of the argument 'directory' and check those
					for file in contents:
						subdir = f"{directory}{self.delimiter}{file}"
						if os.path.isdir(subdir) & (self.found == False) & (subdir not in self.traversed) & (depth < self.depth_max):
							self.forward_prop(subdir, depth + 1)
			# Target is a file or folder
			else:
				# Same as the last one, but only check if the file is in the contents of 'directory'
				# Faster, doesn't require os module which can slow the search down a lot
				if self.target in contents:
					self.tpath = directory
					self.found = True
				else:
					listing = []
					for file in contents:
						subdir = f"{directory}{self.delimiter}{file}"
						if os.path.isdir(subdir) & (self.found == False) & (subdir not in self.traversed) & (depth < self.depth_max):
							self.forward_prop(subdir, depth + 1)
		except Exception as e:
			print(f"Error @ {directory}: {e}")

	def _backward_prop(self, directory, depth):
		try:
			# Break the directory up into its previous directories
			# Drop the current directory part
			partial = directory.split(self.delimiter)[:-1]
			# Join list into string using the delimiter (e.g. ['', 'User', 'myuser', 'Desktop'] -> /User/myuser/Desktop)
			parent = self.delimiter.join(partial)
			if depth < self.depth_max:
				self.forward_prop(parent, depth + 1)
				if self.found == False:
					self._backward_prop(parent, depth + 1)
		except Exception as e:
			print(f"Error @ {directory}: {e}")

	def _target_check(self, target):
		# Drop slashes at beginning
		if target[0] == self.delimiter:
			target = target[1:]
		# Drop slashes at end
		if target[-1] == self.delimiter:
			target = target[:-1]
		# Check if a relative directory (e.g. /sparro/lib/sparro.py)
		if self.delimiter in target:
			self.relative = True
		return target
	
	def search(self, target, start=Path.cwd(), filepath=False):
		self._reset()
		start = str(start)
		# For formatting purposes, there cannot be a delimiter at the end
		if start[-1] == self.delimiter:
			start = start[:-1]
		self.target = self._target_check(target)
		
		self.forward_prop(start, depth=0)
		if self.found == False:
			self._backward_prop(start, depth=0)

		# If filepath is True, return the absolute path to the file, rather than to the directory that contains the target
		# e.g. /Users/myuser/Desktop/python-projects -> /Users/myuser/Desktop/python-projects/path_finder.py
		if filepath:
			self.tpath += self.delimiter + self.target
			return self.tpath
		else:
			return self.tpath

	def _reset(self):
		self.tpath		= None
		self.found		= False
		self.traversed	= set([])
		self.target		= None
		self.relative	= False

	def swap(self, abspath):
		os.chdir(abspath)


def connect_relative_dir(folder="", back=1):
	# back is the number of previous directories we walk
	# a back of 1 is the current dir's parent directory
	# Ex. cur_dir = /user/john doe/documents/sparro/modules
	# back=0 --> /user/john doe/documents/sparro/modules
	# back=1 --> /user/john doe/documents/sparro
	# back=2 --> /user/john doe/documents

	cwd = Path.cwd()
	mod_path = Path(__file__).parent

	if folder != "":
		rel_path = f"{'../'*back}{folder}"
	else:
		rel_path = f"{'../'*back}"

	src_path = (mod_path / rel_path).resolve()
	
	if os.path.isdir(src_path):
		os.chdir(src_path)
	else:
		os.mkdir(src_path)
		os.chdir(src_path)


class TimerError(Exception):
	"""A custom exception used to report errors in use of Timer class"""


class Timer:
	def __init__(self):
		self._start_time = None

	def start(self):
		"""Start a new timer"""
		if self._start_time is not None:
			raise TimerError(f"Timer is running. Use .stop() to stop it")

		self._start_time = time.perf_counter()

	def stop(self):
		"""Stop the timer, and report the elapsed time"""
		if self._start_time is None:
			raise TimerError(f"Timer is not running. Use .start() to start it")

		elapsed_time = time.perf_counter() - self._start_time
		self._start_time = None
		return float(elapsed_time)


def numericize(text, preserve=True):
	try:
		string = text.translate({ord(c): None for c in '$()/,=+[]}{'})
		if "." in text:
			return float(string)
		else:
			return int(string)
	except Exception:
		if preserve:
			return text
		else:
			return None


def connect_relative_dir(folder="", back=1):
	# back is the number of previous directories we walk
	# a back of 1 is the current dir's parent directory
	# Ex. cur_dir = /user/john doe/documents/sparro/modules
	# back=0 --> /user/john doe/documents/sparro/modules
	# back=1 --> /user/john doe/documents/sparro
	# back=2 --> /user/john doe/documents

	cwd = Path.cwd()
	mod_path = Path(__file__).parent

	if folder != "":
		rel_path = f"{'../'*back}{folder}"
	else:
		rel_path = f"{'../'*back}"

	src_path = (mod_path / rel_path).resolve()
	
	if os.path.isdir(src_path):
		os.chdir(src_path)
	else:
		os.mkdir(src_path)
		os.chdir(src_path)


'''
Scomp (String Component Comparison) function checks to see if a smaller string within an array fits in the target string
'''
def scomp(target, array, delimiter='-'):
	target = f"{delimiter}".join(target.split(delimiter)[:-1])
	if target in array:
		i = array.index(target)
		return array[i]
	elif target == "":
		return ""
	else:
		return scomp(target, array, delimiter=delimiter)


#You can use suppress_stdout() with the following template:
'''
with suppress_stdout():
	*functions*
'''
@contextmanager
def suppress_stdout():
	with open(os.devnull, "w") as devnull:
		old_stdout = sys.stdout
		sys.stdout = devnull
		try:  
			yield
		finally:
			sys.stdout = old_stdout


#You can use redirect_stdout() with the following template:
'''
with redirect_stdout():
	*functions*
'''
@contextmanager
def redirect_stdout():
	import datetime
	pf = PathFinder()
	data_path = pf.search("data")
	if data_path == None:
		data_path = Path.cwd()
	else:
		data_path += "/data"

	basename = os.path.basename(__file__).split(".")[0]
	old_stdout = sys.stdout
	sys.stdout = open(f"{data_path}/redirected_output.txt", "a")
	print(datetime.datetime.now())
	try:
		yield
	finally:
		print("")
		sys.stdout = old_stdout


class PathFinder2:
	delimiter = "/"
	tpath		= None
	found		= False
	traversed	= set([])
	target		= None
	relative	= False
	depth_max 	= 7

	def forward_prop(cls, directory, depth):
		try:
			cls.traversed.add(directory)
			# Get directory contents
			contents = os.listdir(directory)

			# Check if target is in the directory
			# Target is a relative directory
			if cls.relative:
				abs_dir = f"{directory}{cls.delimiter}{cls.target}"
				# Check if this is a valid directory. If yes, stop all recursion
				if os.path.exists(abs_dir):
					cls.tpath = directory
					cls.found = True
				else:
					# If no, list the subdirectories of the argument 'directory' and check those
					for file in contents:
						subdir = f"{directory}{cls.delimiter}{file}"
						if os.path.isdir(subdir) & (cls.found == False) & (subdir not in cls.traversed) & (depth < cls.depth_max):
							cls.forward_prop(cls, subdir, depth + 1)
			# Target is a file or folder
			else:
				# Same as the last one, but only check if the file is in the contents of 'directory'
				# Faster, doesn't require os module which can slow the search down a lot
				if cls.target in contents:
					cls.tpath = directory
					cls.found = True
				else:
					listing = []
					for file in contents:
						subdir = f"{directory}{cls.delimiter}{file}"
						if os.path.isdir(subdir) & (cls.found == False) & (subdir not in cls.traversed) & (depth < cls.depth_max):
							cls.forward_prop(cls, subdir, depth + 1)
		except Exception as e:
			print(f"Error @ {directory}: {e}")

	def _backward_prop(cls, directory, depth):
		try:
			# Break the directory up into its previous directories
			# Drop the current directory part
			partial = directory.split(cls.delimiter)[:-1]
			# Join list into string using the delimiter (e.g. ['', 'User', 'myuser', 'Desktop'] -> /User/myuser/Desktop)
			parent = cls.delimiter.join(partial)
			if depth < cls.depth_max:
				cls.forward_prop(cls, parent, depth + 1)
				if cls.found == False:
					cls._backward_prop(cls, parent, depth + 1)
		except Exception as e:
			print(f"Error @ {directory}: {e}")

	def _target_check(cls, target):
		# Drop slashes at beginning
		if target[0] == cls.delimiter:
			target = target[1:]
		# Drop slashes at end
		if target[-1] == cls.delimiter:
			target = target[:-1]
		# Check if a relative directory (e.g. /sparro/lib/sparro.py)
		if cls.delimiter in target:
			cls.relative = True
		return target
	
	@classmethod
	def search(cls, target, start=Path.cwd(), filepath=False):
		cls._reset(cls)
		start = str(start)
		# For formatting purposes, there cannot be a delimiter at the end
		if start[-1] == cls.delimiter:
			start = start[:-1]
		cls.target = cls._target_check(cls, target)
		
		cls.forward_prop(cls, start, depth=0)
		if cls.found == False:
			cls._backward_prop(cls, start, depth=0)

		# If filepath is True, return the absolute path to the file, rather than to the directory that contains the target
		# e.g. /Users/myuser/Desktop/python-projects -> /Users/myuser/Desktop/python-projects/path_finder.py
		if filepath:
			cls.tpath += cls.delimiter + cls.target
			return cls.tpath
		else:
			return cls.tpath

	def _reset(cls):
		cls.tpath		= None
		cls.found		= False
		cls.traversed	= set([])
		cls.target		= None
		cls.relative	= False
