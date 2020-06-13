'''
Profit computations are derived from a compounding formula that increases buy prices and deceases sell prices
for each unit traded.
pi 		:: 	profit
p_1 	:: 	sell price
p_0		::	buy price
mp_1 	:: 	market sell price
mp_0 	:: 	market buy price
r 		:: 	compound rate
q		::	trade cycle quantity

-- Starting Formulas --
pi = p_1*q - p_0*q
p_0 = mp_0*(1+r)^q
p_1 = mp_1*(1-r)^q

Notes:
	pi becomes modified since this is not capitalizing on stock price changes but rather an exchange rate
change. A reduction in relative value is profitable. Therefore, if the gold per USD at time t_0 (now) is going
to decrease at time t_1, we want to buy now so that each unit of gold is worth more dollars than it was before.


Ex//
	Currency 1 and Currency 2 (C_1 and C_2) have an exchange rate of 1.2 (=C_1/C_2).
Quantity of C_1 currency: q_1 = 10 C_1
The account value of C_1 in C_2 terms is 10/1.2 (q_1*C_1 * (C_2/C_1) = q_1*C_2). If C_1/C_2 decreases to
1.1, our C_2 value becomes 10/1.1.
Value of C_1 in C_2 terms goes from 8.33 -> 9.09
From this we learn that decreases in exchange rates should lead to investments in the numerator currency.
Therefore, the profit stems from the difference in the first and second price (p_0 - p_1).

New pi is 
pi = p_1*q - p_0*q

-> pi = q * mp_1 * (1-r)^q - q * mp_0 * (1+r)^q

dpi/dq = (mp_1 * (1-r)^q + q * mp_1 * (1-r)^q * ln(1-r)) - (mp_0 * (1+r)^q + mp_0 * q * (1+r)^q * ln(1+r))

-> dpi/dq = mp_1*(1-r)^q * (1 + q*ln(1-r)) - mp_0*(1+r)^q * (1 + q*ln(1+r))
'''

from math import log
from model import ARIMA


def gold_to_regional(gold, dollar_rate):
	return gold/dollar_rate

def regional_to_gold(regional, dollar_rate):
	return regional*dollar_rate


class Opt:
	cr = 0.00001
	maxiter = 100
	tolerr = 0.0001

	@classmethod
	def buy_price(cls, mp, v):
		return mp*(1-cls.cr)**v

	@classmethod
	def sell_price(cls, mp, v):
		return mp*(1+cls.cr)**v

	@classmethod
	def profit(cls, p0, p1, v):
		return v * (cls.buy_price(p1, v) - cls.sell_price(p0, v))

	@classmethod
	def profit_derivative(cls, p0, p1, v):
		return  cls.buy_price(p1, v) * (1+log(1-cls.cr)*v) - cls.sell_price(p0, v) * (1+log(1+cls.cr)*v)

	@classmethod
	def bisect(cls, p0, p1, xb, xa=0, tolerr=tolerr, maxiter=maxiter, compound_rate=cr):
		'''
		Typical bisection algorithm optimizing for dpi/dq = 0
		https://en.wikipedia.org/wiki/Bisection_method

		For profit bisection we're determining quantity based on an estimated future
		price. xa is our floor and we cannot have a quantity < 0
		xb is our ceiling quantity.

		Bisection works by incrementally decreasing the ceiling and/or increasing the
		floor. Whether to shift the floor or ceiling is deciding by the product of
		the floor and the midpoint (xc).

		If f(xa) * f(xc) is negative, there is an f(x)=0 between xa and xc so we shift
		xb down. If the product is positive, both are the same sign. We shift xa up.

		Repeat this util the change between xc values is less than our tolerable error
		'''
		i = 0
		abserr = xb - xa
		xc_old = 0.75*(xa + xb)

		while (abserr >= tolerr) & (i <= maxiter):
			xc = 0.5*(xa + xb)

			fafc = cls.profit_derivative(p0=p0, p1=p1, v=xa) * cls.profit_derivative(p0=p0, p1=p1, v=xc)

			if fafc < 0:
				xb = xc
			else:
				xa = xc

			abserr = abs((xc-xc_old)/xc_old)
			i += 1
			xc_old = xc

		return int(xc)

	def __call__(cls, *args, **kwargs):
		return cls.bisect(*args, **kwargs)


class Decision:
	def __init__(self, p0, p1, pred, tradetype, tprice, volume=0):
		self.price = p0
		self.price_lag1 = p1
		self.prediction = pred
		self.tradetype = tradetype
		self.trade_price = tprice
		self.volume = volume

	@property
	def array(self):
		return [self.price, self.price_lag1, self.prediction, self.tradetype, self.trade_price, self.volume]


def evaluate(mp, prediction, regionbank, prior_dcs, token):
	'''
	marketprice: Currency Object
	

	Trading strategy is based on profit-optimized quantities, mean-reversion, and
	ARIMA modelling.

	1. Check the prior decision.
		- If the prior decision was to buy, we will immediately sell. 
		- Else, decide whether to buy or hold
	2. Evaluate Gold/Dollar change.
		- If Gold/Dollar is expected to decrease, buy gold so we can revert
		  at the next moment
	3. Evaluate quantity to buy.
		- Use the prediction and current market price
	4. Build decision object and return it
	'''

	# By prebuilding with the default to 'Hold', we must remember to update the
	# tradetype, tprice, and volume attributes
	dcs = Decision(p0=mp,
					p1=prior_dcs.price,
					pred=prediction,
					tradetype="hold",
					tprice=mp,
					volume=0)

	# Sell
	if prior_dcs.tradetype == "buy":
		# Compute selling price
		trade_price = Opt.sell_price(mp=mp, v=prior_dcs.volume)

		dcs.trade = True
		dcs.tradetype = "sell"
		dcs.trade_price = trade_price
		dcs.volume = prior_dcs.volume

	else:
		# The exchange rate (gold per 15 usd) is expected to decrease
		# Buy
		if mp > prediction:
			volume = Opt.bisect(p0=prediction, p1=mp, xb=regionbank.value/token)
			trade_price = Opt.buy_price(mp=mp, v=volume)

			dcs.tradetype = "buy"
			dcs.trade_price = trade_price
			dcs.volume = volume
		else:
			pass

	return dcs



