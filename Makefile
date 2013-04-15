all:
	#python btccharts-arbitrage.py --nodownload --printmk --currency USD --reldiff 4
	python btccharts-arbitrage.py --nodownload --printmk --currency EUR --reldiff 4

EUR:
	python btccharts-arbitrage.py --nodownload --printmk --currency EUR --reldiff 4

USD:
	python btccharts-arbitrage.py --nodownload --printmk --currency USD --reldiff 4

#offline:
#	python btccharts-arbitrage.py --nodownload --printmk
#	python btccharts-arbitrage.py --nodownload --printmk --currency USD --reldiff 5
#	python btccharts-arbitrage.py --nodownload --printmk --markets "mtgoxUSD bitstampUSD btceUSD bitfloorUSD"
