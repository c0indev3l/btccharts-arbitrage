#!/usr/bin/env bash
echo "Running bitcoincharts-arbitrage for USD"
screen -h 1000 -t btccharts-arbitrageUSD 14 bash /home/pi/bitcoin/arbitrage/btccharts-arbitrage/run_arbitrage.sh USD
delay=120
echo "Waiting $delay"
sleep $delay
echo "Running bitcoincharts-arbitrage for EUR"
screen -h 1000 -t btccharts-arbitrageEUR 15 bash /home/pi/bitcoin/arbitrage/btccharts-arbitrage/run_arbitrage.sh EUR
