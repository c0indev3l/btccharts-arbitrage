from email_notifier import Email_Notifier
from pushover_notifier import Pushover_Notifier

def send_email_arbitrage(arb_obj):
  #print("Sending email...")
  str = arbitrage_message_email(arb_obj)
  Nopp = len(arb_obj.df_arbitrage_opportunities)
  
  body = """Hello,

I'm btccharts-arbitrage bot. I'm working for you!
{Nopp} {symbol} arbitrage opportunities have been found with http://www.bitcoincharts.com data.
We are only looking for arbitrage opportunities better than {arbitrage_rel_min}%.
Use this at your own risk!

You should have a look at market depth!!!


========

{str}
""".format(Nopp=Nopp, symbol=arb_obj.symbol, str=str, arbitrage_rel_min=arb_obj.arbitrage_rel_min)


  title = "{Nopp} {symbol} arbitrage opportunities found".format(Nopp=Nopp, symbol=arb_obj.symbol)

  arb_obj.email_notifier.sendEmail(title, body) # ToFix: sending monospace HTML email

def arbitrage_message(arb_obj):
  str = ''
  for i in range(len(arb_obj.df_arbitrage_opportunities)):
    market_buy = arb_obj.df_arbitrage_opportunities.index[i][0]
    market_sell = arb_obj.df_arbitrage_opportunities.index[i][1]
    str = str + "opportunity - buy {size}{cur1} at {ask:.5f}{cur2} ({market_buy}) - sell at {bid:.5f}{cur2} ({market_sell}) - {arbitrage_rel:.2f}% - {arbitrage_abs:.2f}{cur2}\n".format(
      size=arb_obj.size,
      cur1=arb_obj.cur1, cur2=arb_obj.cur2,
      market_sell=market_sell, market_buy=market_buy,
	  ask=arb_obj.df_ask[market_sell][market_buy], bid=arb_obj.df_bid[market_sell][market_buy],
  	  arbitrage_rel=arb_obj.df_arbitrage_rel[market_sell][market_buy],
	  arbitrage_abs=arb_obj.df_arbitrage_abs[market_sell][market_buy])
  return(str)

def arbitrage_message_email(arb_obj):
  str = ''
  
  Nopp = len(arb_obj.df_arbitrage_opportunities)

  for i in range(Nopp):
    market_buy = arb_obj.df_arbitrage_opportunities.index[i][0]
    market_sell = arb_obj.df_arbitrage_opportunities.index[i][1]
    str = str + "opportunity - buy {size}{cur1} at {ask:.5f}{cur2} ({market_buy}) - sell at {bid:.5f}{cur2} ({market_sell}) - {arbitrage_rel:.2f}% - {arbitrage_abs:.2f}{cur2}\n".format(
      size=arb_obj.size,
      cur1=arb_obj.cur1, cur2=arb_obj.cur2,
      market_sell=market_sell, market_buy=market_buy,
	  ask=arb_obj.df_ask[market_sell][market_buy], bid=arb_obj.df_bid[market_sell][market_buy],
  	  arbitrage_rel=arb_obj.df_arbitrage_rel[market_sell][market_buy],
	  arbitrage_abs=arb_obj.df_arbitrage_abs[market_sell][market_buy])
    str = str + " BUY  @ " + "http://bitcoincharts.com/markets/{fullmarketname}_depth.html".format(fullmarketname=market_buy) + "\n"
    str = str + " SELL @ " + "http://bitcoincharts.com/markets/{fullmarketname}_depth.html".format(fullmarketname=market_sell) + "\n"
    str = str + "\n"
	  
  str = str + "\n"
  str = str + "="*50 + "\n"
  str = str + "\n"

  for i in range(Nopp):
    market_buy = arb_obj.df_arbitrage_opportunities.index[i][0]
    market_sell = arb_obj.df_arbitrage_opportunities.index[i][1]
    str = str + "opportunity - buy {size}{cur1} at {ask:.5f}{cur2} ({market_buy}) - sell at {bid:.5f}{cur2} ({market_sell}) - {arbitrage_rel:.2f}% - {arbitrage_abs:.2f}{cur2}\n".format(
      size=arb_obj.size,
      cur1=arb_obj.cur1, cur2=arb_obj.cur2,
      market_sell=market_sell, market_buy=market_buy,
	  ask=arb_obj.df_ask[market_sell][market_buy], bid=arb_obj.df_bid[market_sell][market_buy],
  	  arbitrage_rel=arb_obj.df_arbitrage_rel[market_sell][market_buy],
	  arbitrage_abs=arb_obj.df_arbitrage_abs[market_sell][market_buy])
    str = str + "="*30 + "\n"
    str = str + arb_obj.df.ix[market_buy].to_string() + "\n"
    str = str + "="*40 + "\n"
    str = str + arb_obj.df.ix[market_sell].to_string() + "\n"
    str = str + "="*100 + "\n"

  str = str + "Markets" + "\n"
  str = str + "="*20 + "\n"
  str = str + arb_obj.df.to_string() + "\n"
  str = str + "="*100 + "\n"

  str = str + "Arbitrage matrix absolute ({cur2})".format(cur2=arb_obj.cur2) + "\n"
  str = str + "="*20 + "\n"
  str = str + arb_obj.df_arbitrage_abs.to_string() + "\n"
  str = str + "="*100 + "\n"

  str = str + "Arbitrage matrix relative (%)" + "\n"
  str = str + "="*20 + "\n"
  str = str + arb_obj.df_arbitrage_rel.to_string() + "\n"
  str = str + "="*100 + "\n"

  str = str + "Arbitrage list" + "\n"
  str = str + "="*20 + "\n"
  #str = str + arb_obj.df_arbitrage_opportunities.sort('rel diff', ascending=True).to_string() + "\n"
  str = str + arb_obj.df_arbitrage_opportunities_all.sort('rel diff', ascending=True).to_string() + "\n"
  #str = str + "="*100 + "\n"

  return(str)
  



def print_arbitrage(arb_obj):
  #print(arb_obj.df_arbitrage_opportunities)
  str = arbitrage_message(arb_obj)
  print(str)  

def arbitrage_callback(func, arb_obj):
  func(arb_obj)

def send_push_arbitrage(arb_obj):
  Nopp = len(arb_obj.df_arbitrage_opportunities)
  title = "[btccharts-arbitrage] {Nopp} {symbol} >= {arbitrage_rel_min}%".format(
    Nopp=Nopp, symbol=arb_obj.symbol, arbitrage_rel_min=arb_obj.arbitrage_rel_min)
  str = ''
  Nopp = len(arb_obj.df_arbitrage_opportunities)
  for i in range(Nopp):
    market_buy = arb_obj.df_arbitrage_opportunities.index[i][0]
    market_sell = arb_obj.df_arbitrage_opportunities.index[i][1]
    if i!=0:
      str = str + "="*10 + '\n'

    str = str + "{id:02d}/{Nopp:02d} - BUY {size}{cur1} at {ask:.5f}{cur2} ({market_buy})".format(
      Nopp=Nopp, id=i+1, size=arb_obj.size, 
      cur1=arb_obj.cur1, cur2=arb_obj.cur2, 
      market_buy=market_buy,
      ask=arb_obj.df_ask[market_sell][market_buy]
    )
    str = str + '\n' + "SELL at {bid:.5f}{cur2} ({market_sell})".format(
      cur1=arb_obj.cur1, cur2=arb_obj.cur2,
      market_sell=market_sell, 
	  bid=arb_obj.df_bid[market_sell][market_buy]
	)
    str = str + '\n' + "{arbitrage_rel:.2f}% - {arbitrage_abs:.2f}{cur2}\n".format(
      cur2=arb_obj.cur2,
  	  arbitrage_rel=arb_obj.df_arbitrage_rel[market_sell][market_buy],
	  arbitrage_abs=arb_obj.df_arbitrage_abs[market_sell][market_buy]	
	)
	  
  str = str + "="*20 + '\n'
  for i in range(Nopp):
    market_buy = arb_obj.df_arbitrage_opportunities.index[i][0]
    market_sell = arb_obj.df_arbitrage_opportunities.index[i][1]

    str = str + "{id:02d}/{Nopp:02d} BUY @ http://bitcoincharts.com/markets/{fullmarketname}_depth.html".format(fullmarketname=market_buy, Nopp=Nopp, id=i+1) + '\n'
    str = str + "SELL @ http://bitcoincharts.com/markets/{fullmarketname}_depth.html".format(fullmarketname=market_sell) + '\n'
    str = str + '\n'
  
  arb_obj.push_notifier.sendNotification(str, title)