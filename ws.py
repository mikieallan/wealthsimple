"""
File to facilitate all external API calls to Wealthsimple APIs
"""


import requests
import json
import pprint
from env import *
from config import *

class ws:

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

    access_token = data['access_token']
    identityId = data['identity_canonical_id']
    bearer = "Bearer " + access_token
    cookies = r.cookies

    if otp!=0:
      return bearer, identityId, cookies, r.headers['x-wealthsimple-otp-claim']

    return bearer, identityId, cookies

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

  ### GET WATCHLIST GRAPHQL
  def getWatchListV2(token, identityId, cookies):
    url = GRAPHQL_BASE_URL 
    headers = {
        "content-type": "application/json",
        "authorization": token,
        "X-Ws-Profile-Id": "trade",
        "X-Ws-Session-Id": SESSION_ID
    }

    payload = json.dumps({
      "operationName": "FetchWatchlist",
      "variables": {
        "identityId": identityId,
        "cursor": None
      },
      
      "query": 'query FetchWatchlist($identityId: ID!, $first: Int, $after: String, $sort: WatchedSecuritySort) {\n  identity(id: $identityId) {\n    watchedSecurities(first: $first, after: $after, sort: $sort) {\n      totalCount\n      edges {\n        node {\n          id\n          active\n          activeDate\n          allowedOrderSubtypes\n          buyable\n          sellable\n          currency\n          depositEligible\n          inactiveDate\n          historicalQuotes(timeRange: \"1d\") {\n            adjustedPrice\n            currency\n            date\n            securityId\n            time\n            __typename\n          }\n          quote {\n            amount\n            currency\n            last\n            open\n            previousClose\n            securityId\n            __typename\n          }\n          securityType\n          status\n          stock {\n            description\n            name\n            primaryMic\n            symbol\n            ipoState\n            primaryExchange\n            usPtp\n            __typename\n          }\n          wsTradeEligible\n          wsTradeIneligibilityReason\n          optionsEligible\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n'
    })

    r = requests.post(url, headers=headers, data=payload)
    
    data = r.json()
    edges = data['data']['identity']['watchedSecurities']['edges']
    watchlist_list = []

    for node in edges:
        this_node = node['node']
        watchlist_list.append(this_node)

    return watchlist_list 

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