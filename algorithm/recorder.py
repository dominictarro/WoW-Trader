import os
import utils

class Batch:
	def __init__(self, fn, size=500, dirpath=""):
		if os.path.isdir(dirpath):
			self.dirpath = dirpath
		else:
			if dirpath is "":
				self.dirpath = str(utils.Path.cwd())
			else:
				self.dirpath = self._adjudicate_nearest_path(dirpath)

		self._fn = fn
		self._size = size
		self.batch = []
		self._fp = f"{self.dirpath}/{self._fn}"

		self._initialize_file()

	def _initialize_file(self):
		with open(self._fp, "w") as f:
			line = "time,market_price,prior_price,prediction,trade,tradeprice,volume,regionbank,wowbank,taper,runtime"
			f.write(line)

	def _adjudicate_nearest_path(self, dirpath):
		curdir = utils.Path.cwd()
		pf = utils.PathFinder()
		loc = pf.search(dirpath, filepath=True)
		if loc is None:
			raise utils.PathError(f"{dirpath} not found within {pf.depth_max} recursions")
		return loc

	def record(self, time, regionbank, wowbank, dcs, taper, runtime):
		array = list(dcs.array)
		array.extend([regionbank.value, wowbank.value, taper, runtime])
		array.insert(0,time)

		self.batch.append(array)

		if len(self.batch) == self._size:
			self.store()

	def store(self):
		out = "\n" + "\n".join([",".join([str(x) for x in array]) for array in self.batch])
		'''
		'out' should go from
		[
			[05-21-2020, 121912, ..., 0.075413],
			...,
			[06-11-2020, 128334, ..., 0.043629]
		]

		to
		"
		05-21-2020,121912,...,0.075413
		...
		06-11-2020,128334,...,0.043629
		"
		'''
		with open(self._fp, "a") as f:
			f.write(out)

		self.batch = []


