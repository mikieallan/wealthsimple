import requests
import sys
import json
import pprint
from env import *
from config import *


class wSimple:

# EXTERNAL API CALLS

  ### LOGIN
  def login(otp=0, username=USERNAME, password=PASSWORD):
    url = BASE_URL + LOGIN_ENDPOINT
    if (otp == 0):
      headers = {
          "Content-Type": "application/json",
          "x-wealthsimple-otp-claim": OTP_CLAIM,
          "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
      }
    else:
      headers = {
          "Content-Type": "application/json",
          "x-wealthsimple-otp": otp + ";remember=true",
          "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
      }

    payload = json.dumps(dict(
        grant_type="password",
        username=USERNAME,
        password=PASSWORD,
        skip_provision=True,
        scope=SCOPES,
        client_id=CLIENT_ID
    ))

    r = requests.post(url, data=payload, headers=headers)
    data = r.json()
    #print(data)

    access_token = data['access_token']
    refresh_token = data['refresh_token']
    user_invest_id = data['profiles']['invest']['default']
    user_trade_id = data['profiles']['trade']['default']
    bearer = "Bearer " + access_token

    if otp!=0:
      return bearer, r.headers['x-wealthsimple-otp-claim']

    return bearer

  ### SWITCH TO TRADE
  def switchToTrade(prev_token):
    url = BASE_URL + SWITCH_ENDPOINT
    headers = {
        "content-type": "application/json",
        "authorization": prev_token,
    }
    payload = json.dumps(dict(
        profile="trade",
        scope="invest.read invest.write trade.read trade.write tax.read tax.write",
        client_id=TRADE_CLIENT_ID
    ))

    r = requests.post(url, data=payload, headers=headers)
    data = r.json()

    updated_access_token = data['access_token']
    bearer = "Bearer " + updated_access_token

    return bearer

  ### GET WATCHLIST
  def getWatchlist(token):
    url = TRADE_BASE_URL + WATCHLIST_ENDPOINT

    headers = {
        "content-type": "application/json",
        "authorization": token,
    }

    r = requests.get(url, headers=headers)
    watchlist = r.json()
    securities = watchlist['securities']

    return securities

  ### GET ACCOUNT HOLDINGS
  def getAccountHoldings(token):

    url = TRADE_BASE_URL + ACCOUNT_LIST_ENDPOINT

    headers = {
        "content-type": "application/json",
        "authorization": token,
    }

    r = requests.get(url, headers=headers)
    accounts = r.json()
    account_list = accounts['results']

    my_holdings = {}

    for i in range(len(account_list)):
        acct = account_list[i]['id']
        my_holdings[acct] = { 'type': account_list[i]['account_type'], 'cash': {'value': account_list[i]['current_balance']['amount']}}
        
        for key in account_list[i]['position_quantities']:
            my_holdings[acct][key] = {'quantity': account_list[i]['position_quantities'][key]}

    return my_holdings

  ### GET POSITIONS
  def getPositions(token, my_holdings):

    url = TRADE_BASE_URL + POSITIONS_ENDPOINT

    headers = {
        "content-type": "application/json",
        "authorization": token,
    }

    r = requests.get(url, headers=headers)
    positions = r.json()['results']

    for i in range(len(positions)):
        account_id = positions[i]['account_id']
        stock_id = positions[i]['id']
        my_holdings[account_id][stock_id]['symbol'] =  positions[i]['stock']['symbol']
        my_holdings[account_id][stock_id]['price'] = positions[i]['quote']['amount']
        my_holdings[account_id][stock_id]['value'] = round(float(my_holdings[account_id][stock_id]['price']) * my_holdings[account_id][stock_id]['quantity'],2)
        
    account_totals = {}

    for key in my_holdings:
        account_totals[key] = 0
        
        for key2 in my_holdings[key]:
            if isinstance(my_holdings[key][key2], dict):
                account_totals[key] += my_holdings[key][key2]['value']
        
    for key in my_holdings:
        my_holdings[key]['total'] = round(account_totals[key],2)

    return my_holdings

  ### EXECUTE MARKET BUY ORDER
  def buy(token, acc_id, sec_id, quantity, price):
    url = TRADE_BASE_URL + ORDERS_ENDPOINT

    headers = {
        "content-type": "application/json",
        "authorization": token,
    }

    payload = json.dumps(dict(
        account_id = acc_id,
        security_id = sec_id,
        order_type = "buy_quantity",
        order_sub_type = "market",
        time_in_force = "day",
        market_value = price,
        quantity = quantity,
        limit_price = round(price * 1.05,2)
    ))

    # print(url)
    # pprint.pprint(payload)
    # pprint.pprint(headers)

    r = requests.post(url, data=payload, headers=headers)
    data = r.json()

    return data

# NO EXTERNAL CALLS


  ### GET PERSONAL PRE-SET PORTFOLIO
  def getMyPresets():
    return ETF_LIST


  ### CREATE DICTIONARY OF PRESET ETFS AND THEIR VALUES
  def createEtfDict(securities, etfs):

    etf_dict = {}

    for i in range(len(securities)):
        if securities[i]['stock']['symbol'] in etfs:
            etf_dict[securities[i]['stock']['symbol']] = {
                "id": securities[i]['id'],
                "price": securities[i]['quote']['amount']
            }

    return etf_dict

  ### GET CURRENT PORTFOLIO BALANCE
  def getCurrentPortfolioBalance(account, etf_dict, my_holdings):

    etf_id_dict = {}
    etf_id_list = [] # Mask for easy filtering, should improve
    total = 0

    for key in etf_dict:
      etf_id_list.append(etf_dict[key]['id'])
    
    # Create dictionary with key as ETF ID containing ETF value, symbol, and desired weighting
    for key in my_holdings[account]:
      if key in etf_id_list:
        total += float(my_holdings[account][key]['value'])
        etf_id_dict[key] = {}
        etf_id_dict[key]['value'] = float(my_holdings[account][key]['value'])
        etf_id_dict[key]['price'] = float(my_holdings[account][key]['price'])
        etf_id_dict[key]['symbol'] = my_holdings[account][key]['symbol']
        etf_id_dict[key]['desired_weighting'] = ETF_LIST[my_holdings[account][key]['symbol']]

    # Calculate current ratio and difference from desired
    for key in etf_id_dict:
      etf_id_dict[key]['current_ratio'] = etf_id_dict[key]['value'] / total
      etf_id_dict[key]['delta_to_target'] = (etf_id_dict[key]['current_ratio'] - etf_id_dict[key]['desired_weighting']) / etf_id_dict[key]['desired_weighting']

    #pprint.pprint(etf_id_dict)

    return etf_id_dict


  ### CALCULATE SHARES TO PURCHASE
  def getSharesToPurchase(acct_holdings, etf_id_dict, amount_to_contribute, print_current):

    # Get amount to contribue 
    
    total = amount_to_contribute
    money_remaining = amount_to_contribute;

    for key in etf_id_dict:
      total += etf_id_dict[key]['value']

    # Find cheapest possible thing to buy and update ratios with new total
    cheapest_buy = float(etf_id_dict[list(etf_id_dict.keys())[0]]['price'])
    for key in etf_id_dict:
      etf_id_dict[key]['current_ratio'] = etf_id_dict[key]['value'] / total
      etf_id_dict[key]['delta_to_target'] = (etf_id_dict[key]['current_ratio'] - etf_id_dict[key]['desired_weighting']) / etf_id_dict[key]['desired_weighting']
      if etf_id_dict[key]['price'] < cheapest_buy:
        cheapest_buy = etf_id_dict[key]['price']


    ## NOTE: Am assuming will never sell, thus skipping checks for overweighting

    sorted_list = list(etf_id_dict.keys())
    sorted_list = sorted(sorted_list, key=lambda x: (etf_id_dict[x]['delta_to_target']))

    if (print_current):
      print("\n\nDeltas to target (where delta = (current % - desired % ) / desired % ):")
      for i in range(len(sorted_list)):
        print(etf_id_dict[sorted_list[i]]['symbol'] + ": " + str(round(etf_id_dict[sorted_list[i]]['delta_to_target']*100,2)))
    

    for key in etf_id_dict:
      etf_id_dict[key]['to_buy'] = 0
    
    # while there's money remaining, continue looping

    while (money_remaining >= cheapest_buy):
      for i in range(len(sorted_list)):

        # Check if affordable
        if etf_id_dict[sorted_list[i]]['price'] <= money_remaining: 
          
          #print("\n" + etf_id_dict[sorted_list[i]]['symbol'] + ": " + str(etf_id_dict[sorted_list[i]]['price']) + "\n")
          
          # update list of what to buy, money remaining, the current weighting, and the delta
          etf_id_dict[sorted_list[i]]['to_buy'] += 1
          money_remaining -= etf_id_dict[sorted_list[i]]['price']
          updated_value = etf_id_dict[sorted_list[i]]['to_buy']*etf_id_dict[sorted_list[i]]['price']+etf_id_dict[sorted_list[i]]['value']
          etf_id_dict[sorted_list[i]]['value'] = updated_value
          etf_id_dict[sorted_list[i]]['current_ratio'] = etf_id_dict[sorted_list[i]]['value'] / total
          etf_id_dict[sorted_list[i]]['delta_to_target'] = (etf_id_dict[sorted_list[i]]['current_ratio'] - etf_id_dict[sorted_list[i]]['desired_weighting']) / etf_id_dict[sorted_list[i]]['desired_weighting']
          
          # Re-sort based on updated values
          sorted_list = sorted(sorted_list, key=lambda x: (etf_id_dict[x]['delta_to_target']))

          # Print values to double check
          # for i in range(len(sorted_list)):
          #   print(etf_id_dict[sorted_list[i]]['symbol'] + ": " + str(round(etf_id_dict[sorted_list[i]]['delta_to_target'],3)))
    
          break

    return etf_id_dict, money_remaining
