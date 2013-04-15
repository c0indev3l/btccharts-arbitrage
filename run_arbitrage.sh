#!/usr/bin/env bash
CURRENCY=$1
DIR=/home/pi/bitcoin/arbitrage/btccharts-arbitrage/
while true
do
		python ${DIR}btccharts-arbitrage.py --printmk --currency $CURRENCY --reldiff 7 --loop 300 --sendpush --arbitrage --nodownload #--sendemail # 2>&1 | tee /tmp/btccharts-arbitrage_$CURRENCY.log
		DELAY=120
		echo "Restart after $DELAY s"
		sleep $DELAY
done
