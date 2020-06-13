import accounts
from model import ARIMA
import recorder
import evaluator
import utils
import pandas as pd


def get_data(file):
	fp = utils.PathFinder2.search(file)
	utils.os.chdir(fp)

	with open(file, "r") as f:
		df = pd.read_csv(f, index_col='time', infer_datetime_format=True)
		df['pdelta'] = df['price'].diff(periods=1)
		df.drop(df.index[0], inplace=True)
	
	return df.itertuples()


def algo(file, start_regional, region, start_gold, token, outfile):
	timer = utils.Timer()

	data 	= get_data(file)
	model 	= ARIMA()
	regionbank	= accounts.Account(start_regional, region)
	wowbank	= accounts.Account(start_gold, "WoW")
	records	= recorder.Batch(fn=outfile, dirpath="data")

	dcs = evaluator.Decision(p0=0,
							p1=0,
							pred=0,
							tradetype="hold",
							tprice=0,
							volume=0)

	for i, row in enumerate(data):

		time = row[0]
		price = float(row[1])
		timer.start()
		# Trading script begins here
		pred = model.next(price)

		# Need to load the model with initial values
		if i < 5:
			timer.stop()
			dcs = evaluator.Decision(p0=price,
									p1=price,
									pred=pred,
									tradetype="hold",
									tprice=price,
									volume=0)
			continue

		dcs = evaluator.evaluate(mp=price,
								prediction=price+pred,
								regionbank=regionbank,
								prior_dcs=dcs,
								token=token)

		# 'taper' will count volume decreased during a sale when there isn't enough in the
		# WoW account to sell at the suggested volume
		taper = 0
		if dcs.tradetype is "buy":
			cost = token * dcs.volume
			gain = dcs.trade_price * dcs.volume

			regionbank.withdraw(cost)
			wowbank.deposit(gain)
			
		elif dcs.tradetype is "sell":
			cost = dcs.trade_price * dcs.volume
			gain = token * dcs.volume

			try:
				regionbank.deposit(gain)
				wowbank.withdraw(cost)
			except RuntimeError:
				while cost > wowbank.value:
					taper += 1
					dcs.volume -= 1
					dcs.trade_price = evaluator.Opt.sell_price(price, dcs.volume)
					cost = dcs.trade_price * dcs.volume
					regionbank.withdraw(token)
				wowbank.withdraw(cost)


			# Move profits to regional
			if wowbank.value > price:
				q = int(wowbank.value/price) - 1
				regionbank.deposit(token*q)
				wowbank.withdraw(q*price)


		records.record(time=time,
					regionbank=regionbank,
					wowbank=wowbank,
					taper=taper,
					dcs=dcs,
					runtime=timer.stop())

		#print(dcs.tradetype, dcs.price)
	print(regionbank.value + evaluator.gold_to_regional(wowbank.value, price/token))


if __name__ == '__main__':
	algo(file="eu-token-full.csv",
		start_regional=1000,
		region="EU",
		start_gold=200000,
		token=20,
		outfile="testrun.txt")

