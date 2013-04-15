#!/usr/bin/env python

import argparse
import os
import sys
import json
import urllib2
from time import sleep
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from arbitrage_callback import *

class BitcoinChartsMarkets:
  def __init__(self, args):
    self.args = args
    self.url = "http://bitcoincharts.com/t/markets.json"
    self.size = 1
    self.cur1 = 'BTC'
    
    if args.currency!=None:
      self.cur2 = args.currency.upper()
      self.symbol = "{cur1}{cur2}".format(cur1=self.cur1, cur2=self.cur2)
    else:
      if args.arbitrage:
        print("use '--currency USD' or '--currency EUR'")
        sys.exit(1)
    
    self.email_notifier = Email_Notifier(self.args)
    self.push_notifier = Pushover_Notifier(self.args)

        
  def update(self, args):
    dt_now = datetime.now()
    print("="*10+" Running Bitcoincharts-arbitrage @ {dt} ".format(dt=dt_now.strftime("%Y-%m-%d %H:%M"))+"="*10) 

    try:
      if not args.nodownload:
        self.download()
        self.write_json()
      else:
        self.read_json()
    except:
      print("Can't update data now (probably too many request)")
      return()

    if args.printjson:
      self.pretty_print_json()
    
    self.convert_to_DataFrame()

    self.df.to_csv(os.path.join(self.args.basepath, "data/out/_ALL_symbols.csv"))
    
    if args.currency!=None:
      self.market_filter(args)
    
    if args.printmk:
      print(list(self.df.index))
      print("="*10+" Symbols (currency_volume descending)"+"="*10)
      print(self.df)
      print("="*10+" Asks (ascending)"+"="*10)
      print(self.df.sort('ask', ascending=True))
      print("="*10+" Bids (descending)"+"="*10)
      print(self.df.sort('bid', ascending=False))

    if args.currency!=None:
      self.df.to_csv(os.path.join(self.args.basepath, "data/out/{symbol}_symbols.csv".format(symbol=self.symbol)))
    
    if args.currency!=None and args.arbitrage:
      self.arbitrage(args) 

  def download(self):
    print("="*10+" Downloading market data from {url} (please wait) ".format(url=self.url)+"="*10)
    response = urllib2.urlopen(self.url)
    self.json_data = response.read()
    self.data = json.loads(self.json_data)
    
  def write_json(self):
    filename = os.path.join(self.args.basepath, "data/bitcoincharts_markets.json")
    print("Writing market data to file \"{filename}\"".format(filename=filename))
    myFile = open(filename, 'w')
#    myFile = open("data/bitcoincharts_markets.json", 'w')
    myFile.write(self.json_data)
    myFile.close()

  def read_json(self):
    filename = os.path.join(self.args.basepath, "data/bitcoincharts_markets.json")
    myFile = open(filename, 'r')
    print("="*10+" Reading market data from file \"{filename}\" ".format(filename=filename)+"="*10)
    self.json_data = myFile.read()
    self.data = json.loads(self.json_data)
    myFile.close()

  def pretty_print_json(self):
    #print(self.data)
    print(json.dumps(self.data, sort_keys=True, indent=2))

  def convert_to_DataFrame(self):
    self.df = pd.DataFrame(self.data)
    #del self.df.ix['symbol'] # remove first line (only symbol) ToFix
    self.df.index = self.df['symbol'] # change index to marketname (symbol)
    self.df['latest_trade'] = self.df['latest_trade'].map(datetime.utcfromtimestamp) # cast unixtime to python datetime

    del self.df['symbol'] # remove symbol column
    self.df['spread'] = self.df['ask'] - self.df['bid']

  def market_filter(self, args):
    if self.cur2!=None: # filter using currency arg
      self.df = self.df[self.df['currency']==self.cur2]
      
    if args.markets!=None: # filter using markets list
      markets = args.markets.split(' ')
      self.df =  self.df.ix[markets]
    
    #self.df = self.df[self.df['currency_volume']!=0.0] # remove symbols without volume
    # remove NaN
    # use np.isifinite (or np.isnan)
    if not args.shownan:
      #mask = (self.df['bid'].apply(np.isfinite)) | (self.df['ask'].apply(np.isfinite))
      #mask =  ~ (self.df['bid'].isnull() & self.df['ask'].isnull())
      mask = ((self.df['ask']>0.0) & (self.df['bid']>0.0))
      self.df = self.df[mask]
      
    # Remove inactive markets (latest_trade)
    dt_inactive = datetime.now() - timedelta(days=7)
    print("="*40)
    mask = self.df['latest_trade'] > dt_inactive
    self.df = self.df[mask]
    
    # sort market
    self.df = self.df.sort('latest_trade', ascending=False)
    self.df = self.df.sort('currency_volume', ascending=False)
    
  def arbitrage(self, args):
    print("="*10+" Tickers "+"="*10)

    self.markets = self.df.index

    self.df_ask = pd.DataFrame(index=self.markets, columns=self.markets)
    self.df_bid = pd.DataFrame(index=self.markets, columns=self.markets)
    
    dt_now = datetime.now()
    str = "Ticker bid/ask @ {dt}".format(dt=dt_now.strftime("%Y-%m-%d %H:%M"))

    for mk in self.markets:
      str = str + " - {market}: {bid:.5f}/{ask:.5f}".format(market=mk, bid=self.df.ix[mk]['bid'], ask=self.df.ix[mk]['ask'])
      self.df_ask.ix[mk] = self.df.ix[mk]['ask'] # ToImprove: this can probably be done outside this for loop
      self.df_bid[mk] = self.df.ix[mk]['bid'] # ToImprove: this can probably be done outside this for loop
    print(str)

    self.df_arbitrage_abs = (self.df_bid - self.df_ask) #*self.size
    self.df_arbitrage_rel = (self.df_bid - self.df_ask)/self.df_ask*100.0
    
    self.df_arbitrage_abs.to_csv(os.path.join(self.args.basepath, "data/out/{symbol}_arbitrage_abs.csv".format(symbol=self.symbol)))
    self.df_arbitrage_rel.to_csv(os.path.join(self.args.basepath, "data/out/{symbol}_arbitrage_rel.csv".format(symbol=self.symbol)))


    if self.args.reldiff==None:
      self.arbitrage_rel_min = 0.0 # filter (%)
    else:
      self.arbitrage_rel_min = float(self.args.reldiff)

    #df_arbitrage_opportunities = df_arbitrage_rel>0

    #lst_arbitrage_opportunities = list(df_arbitrage_rel[df_arbitrage_rel>0])
    #lst_arbitrage_opportunities.sort(reverse=True)

    #print("Ask")
    #print(self.df_ask)
    #print("Bid")
    #print(self.df_bid)
    #print("Diff abs")
    #print(self.df_arbitrage_abs)

    print("="*10+" Relative difference (%) "+"="*10)
    print(self.df_arbitrage_rel)

    print("="*40)
    #df_arbitrage_opportunities df_arbitrage_opportunities
    
    #self.df_arbitrage_opportunities_all = pd.DataFrame(self.df_arbitrage_rel.unstack(), columns=['rel diff'])
    self.df_arbitrage_opportunities_all = pd.DataFrame(self.df_ask.unstack(), columns=['ask'])
    #self.df_arbitrage_opportunities_all['ask'] = self.df_ask.unstack()
    self.df_arbitrage_opportunities_all['bid'] = self.df_bid.unstack()
    self.df_arbitrage_opportunities_all['abs diff'] = self.df_arbitrage_abs.unstack()
    self.df_arbitrage_opportunities_all['rel diff'] = self.df_arbitrage_rel.unstack()
    self.df_arbitrage_opportunities_all = self.df_arbitrage_opportunities_all[self.df_arbitrage_opportunities_all['rel diff']>-100]
    self.df_arbitrage_opportunities_all = self.df_arbitrage_opportunities_all.sort('rel diff', ascending=False)
    self.df_arbitrage_opportunities_all.index.names = ['market_sell', 'market_buy']
    self.df_arbitrage_opportunities_all = self.df_arbitrage_opportunities_all.swaplevel(0, 1, axis=0) # swap to have market_buy as first hierarchical index
    self.df_arbitrage_opportunities_all.sort('rel diff', ascending=False).to_csv(os.path.join(self.args.basepath, "data/out/{symbol}_arbitrage_rel_lst.csv".format(symbol=self.symbol)))
    print(self.df_arbitrage_opportunities_all.sort('rel diff', ascending=True)[-50:])
    
    print("="*10+" Arbitrage opportunities (better than {arbitrage_rel_min}%)".format(arbitrage_rel_min=self.arbitrage_rel_min)+"="*10)
    self.df_arbitrage_opportunities = self.df_arbitrage_opportunities_all[self.df_arbitrage_opportunities_all['rel diff']>self.arbitrage_rel_min]
    
    if len(self.df_arbitrage_opportunities)>0:
      arbitrage_callback(print_arbitrage, self)
      if self.args.sendemail:
        arbitrage_callback(send_email_arbitrage, self)
      if self.args.sendpush:
        arbitrage_callback(send_push_arbitrage, self)      
      
    else:
      print(";-( no arbitrage opportunities found with BitcoinCharts ;-(")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Use the following parameters')
  parser.add_argument('--nodownload', action='store_true', help='use this flag to avoid download data (will use a previously downloaded file)')
  parser.add_argument('--printjson', action='store_true', help='use this flag to pretty print JSON')
  parser.add_argument('--printmk', action='store_true', help='use this flag to print market DataFrame')
  parser.add_argument('--loop', action='store', help='use this flag to run program in an infinite loop (LOOP parameters is pause in seconds)')
  parser.add_argument('--currency', action='store', help='use this flag to filter using currency (EUR, USD, ...)')
  parser.add_argument('--markets', action='store', help='use this flag to filter using symbol (\"mtgoxUSD bitstampUSD btceUSD bitfloorUSD ...\")')
  parser.add_argument('--reldiff', action='store', help='use this flag to show only arbitrage opportunities >= reldiff (%%)')
  parser.add_argument('--shownan', action='store_true', help='use this flag to print market with nan bid/ask (both)')
  parser.add_argument('--sendemail', action='store_true', help='use this flag to send email when arbitrage opportunities are found')
  parser.add_argument('--sendpush', action="store_true", help="use this flag to send push notification")
  parser.add_argument('--debug', action="store_true", help="use this flag to switch to debug mode")
  parser.add_argument('--test', action="store_true", help="use this flag to test notification (email, SMS, push...)")
  parser.add_argument('--arbitrage', action='store_true', help='use this flag to calculate arbitrage opportunities')
  args = parser.parse_args()
  
  args.basepath = os.path.dirname(__file__)
  
  btcmk = BitcoinChartsMarkets(args)

  if args.loop==None:
    btcmk.update(args)
  else:
    delay_s = float(args.loop)
    while True:
      btcmk.update(args)
      dt_next = datetime.now() + timedelta(seconds=delay_s)
      print("="*10)
      print("Waiting... next update @ {dt_next}".format(dt_next=dt_next.strftime("%Y-%m-%d %H:%M")))
      sleep(delay_s)