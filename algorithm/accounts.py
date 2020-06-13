
class CurrencyBase:
	def __init__(self, value, name):
		self.value	= value
		self.name	= name

	def __str__(self):
		return f"{self.value}"

	def __repr__(self):
		return f"{self.value} {self.name}"

class Account(CurrencyBase):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def deposit(self, b):
		self.value += b

	def withdraw(self, b):
		if b <= self.value:
			self.value -= b
		else:
			raise RuntimeError(f"Tried to withdraw {b} from an account valued at {self.value}")