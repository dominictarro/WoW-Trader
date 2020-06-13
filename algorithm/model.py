import numpy as np

class ARIMA:
	def __init__(self, ar_params=[1.676390, -0.613328, 0.675564, -1.317306, 0.556450],
						ma_params=[-1.133462, 0.119313, -0.767581, 0.924096, -0.136754]):
		self.ar_params 	= np.array(ar_params)
		self.ma_params 	= np.array(ma_params)

		self.ar_vals	= np.array([0]*len(ar_params))
		self.ma_vals	= np.array([0]*len(ma_params))

		self.prediction = 0
		self.prior_val = 0

	def predict(self):
		return np.dot(self.ar_params, self.ar_vals) + np.dot(self.ma_params, self.ma_vals)

	def compute_error(self, value):
		return value - self.prediction

	def update_priors(self, value):
		error = self.compute_error(value)

		# Shift AR and MA values and insert latest values to the front of arrays
		self.ar_vals = self.ar_vals[:-1]
		self.ar_vals = np.insert(self.ar_vals, 0, values=value)
		self.ma_vals = self.ma_vals[:-1]
		self.ma_vals = np.insert(self.ma_vals, 0, values=error)

	def next(self, value):
		diff = value - self.prior_val
		self.update_priors(diff)
		self.prediction = self.predict()
		self.prior_val = value
		return self.prediction


