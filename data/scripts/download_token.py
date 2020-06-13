import requests, json, datetime, os
from pathlib import Path
import pandas as pd

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


def download():
	link = "https://wowtokenprices.com/history_prices_full.json"
	content = requests.get(link).text
	data_dict = eval(content)
	
	connect_relative_dir(folder="", back=1)
	data = {}
	for region in data_dict.keys():
		price = list(map(lambda x: x['price'], data_dict[region]))
		time = list(map(lambda x: datetime.datetime.fromtimestamp(x['time']), data_dict[region]))
		df = pd.DataFrame({"time": time, "price": price})
		df.to_csv(f"{region}-token-full.csv", index=False)

if __name__ == '__main__':
	download()