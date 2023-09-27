"""
File to calculate values, holding majority of logic
"""



import json
import pprint
from config import *

class ws_helpers:

  ### PRINT ACCOUNT TOTALS
  def printAccountTotals(my_holdings):
    for key in my_holdings:
      print(my_holdings[key]['type'] + ": " + str(my_holdings[key]['total']))
    print("\n=====")

  def printHoldings(my_holdings):
    print(my_holdings)
    for key in my_holdings:
      print(my_holdings[key]['type'] + ": " + str(my_holdings[key]['total']))
      for key2 in my_holdings[key]:
        if (type(my_holdings[key][key2]) == dict):
          if (key2 == "cash"):
            print("  Cash: " + str(my_holdings[key][key2]['value']))
          else:
            print("  " + my_holdings[key][key2]['symbol'] + ": " + str(round(my_holdings[key][key2]['quantity'],2)) + " at " + str(round(float(my_holdings[key][key2]['price']),2)) + ", value: " + str(my_holdings[key][key2]['value']))
    print("\n=====")

  ### GET PERSONAL PRE-SET PORTFOLIO
  def getMyPresets():
    return ETF_LIST

  ### CREATE DICTIONARY OF PRESET ETFS AND THEIR VALUES
  def createEtfDict(watchlist_list, etfs):

    filtered_watchlist = [entry for entry in watchlist_list if entry['stock']['symbol'] in ETF_LIST.keys()]

    ## CHECK IF ALL DESIRED PORTFOLIO FOUND IN WATCHLIST
    if len(filtered_watchlist) != len(ETF_LIST.keys()):
        print("WARNING - Some securities on watchlist not found")
    # else: 
        # print("all watchlist found")

    etf_dict = {}

    for etf in filtered_watchlist:
      etf_dict[etf['id']] = {
        "price": etf['quote']['amount'],
        "symbol": etf['stock']['symbol']
      }
    return etf_dict

  ### GET CURRENT PORTFOLIO BALANCE
  def calculateCurrentPortfolioBalance(etf_dict, holdings):

    # Create dictionary with key as ETF ID containing ETF value, symbol, and desired weighting


    this_account_etfs_dict = {}
    this_account_etfs_dict = etf_dict

    etf_symbols = list(ETF_LIST.keys())

    total_val = 0

    for key, value in holdings.items():
      if "sec" in key:
        if holdings[key]['symbol'] in etf_symbols:
          this_account_etfs_dict[key]['current_quant'] = holdings[key]['quantity']
          this_account_etfs_dict[key]['current_val'] = holdings[key]['value']
          total_val += holdings[key]['value']

    for key, value in this_account_etfs_dict.items():
      current_ratio = float(this_account_etfs_dict[key]['current_val'] / total_val)
      desired_ratio = float(ETF_LIST[this_account_etfs_dict[key]['symbol']])
      this_account_etfs_dict[key]['current_ratio'] = current_ratio
      this_account_etfs_dict[key]['desired_ratio'] = desired_ratio
      
      this_account_etfs_dict[key]['delta_to_target'] = (current_ratio - desired_ratio) / desired_ratio

    return this_account_etfs_dict

  ### CALCULATE SHARES TO PURCHASE
  def calculateSharesToPurchase(holdings, etf_id_dict, amount_to_contribute):

    this_account_etfs_dict = {}
    this_account_etfs_dict = etf_id_dict

    etf_symbols = list(ETF_LIST.keys())

    total_val = 0    

    for key, value in holdings.items():
      if "sec" in key:
        if holdings[key]['symbol'] in etf_symbols:
          this_account_etfs_dict[key]['current_quant'] = holdings[key]['quantity']
          this_account_etfs_dict[key]['current_val'] = holdings[key]['value']
          total_val += holdings[key]['value']

    for key, value in this_account_etfs_dict.items():
      current_ratio = float(this_account_etfs_dict[key]['current_val'] / total_val)
      desired_ratio = float(ETF_LIST[this_account_etfs_dict[key]['symbol']])
      this_account_etfs_dict[key]['current_ratio'] = current_ratio
      this_account_etfs_dict[key]['desired_ratio'] = desired_ratio
      
      this_account_etfs_dict[key]['delta_to_target'] = (current_ratio - desired_ratio) / desired_ratio

    total = amount_to_contribute
    money_remaining = amount_to_contribute

    for key in this_account_etfs_dict:
      total += this_account_etfs_dict[key]['current_val']
      this_account_etfs_dict[key]['price'] = float(this_account_etfs_dict[key]['price'])
      this_account_etfs_dict[key]['future_val'] = this_account_etfs_dict[key]['current_val']

    cheapest_buy = float(this_account_etfs_dict[list(this_account_etfs_dict.keys())[0]]['price'])

    for key in this_account_etfs_dict:
      this_account_etfs_dict[key]['future_ratio'] = this_account_etfs_dict[key]['current_val'] / total
      this_account_etfs_dict[key]['delta_to_target'] = (this_account_etfs_dict[key]['current_ratio'] - this_account_etfs_dict[key]['desired_ratio']) / this_account_etfs_dict[key]['desired_ratio']
      
      if this_account_etfs_dict[key]['price'] < cheapest_buy:
        cheapest_buy = this_account_etfs_dict[key]['price']
            
    sorted_list = list(this_account_etfs_dict.keys())
    sorted_list= sorted(sorted_list, key=lambda x: (this_account_etfs_dict[x]['delta_to_target']))

    print_current = False

    if (print_current):
      print("\n\nDeltas to target (where delta = (current % - desired % ) / desired % ):")
      for i in range(len(sorted_list)):
        print(this_account_etfs_dict[sorted_list[i]]['symbol'] + ": " + str(round(this_account_etfs_dict[sorted_list[i]]['delta_to_target']*100,2)))


    for key in this_account_etfs_dict:
      this_account_etfs_dict[key]['to_buy'] = 0
        
    while (money_remaining >= cheapest_buy):
      for i in range(len(sorted_list)):

      # Check if affordable
        if this_account_etfs_dict[sorted_list[i]]['price'] <= money_remaining: 

          # print("\n" + this_account_etfs_dict[sorted_list[i]]['symbol'] + ": " + str(this_account_etfs_dict[sorted_list[i]]['price']) + "\n")

          ### Update list of what to buy, money remaining, the current weighting, and the delta
            
          # Add one to buy
          this_account_etfs_dict[sorted_list[i]]['to_buy'] += 1
          
          # Remove money from share just added
          money_remaining -= this_account_etfs_dict[sorted_list[i]]['price']
          
          # Update future val to include share just added
          updated_value = this_account_etfs_dict[sorted_list[i]]['price'] + this_account_etfs_dict[sorted_list[i]]['future_val']
          this_account_etfs_dict[sorted_list[i]]['future_val'] = updated_value
          
          # Update future ratio to include share just added
          this_account_etfs_dict[sorted_list[i]]['future_ratio'] = this_account_etfs_dict[sorted_list[i]]['future_val'] / total
          
          # Update delta calculation for all stocks to include newly purchased stock
          for j in range(len(sorted_list)):
              this_account_etfs_dict[sorted_list[j]]['delta_to_target'] = (this_account_etfs_dict[sorted_list[j]]['future_ratio'] - this_account_etfs_dict[sorted_list[j]]['desired_ratio']) / this_account_etfs_dict[sorted_list[j]]['desired_ratio']

          # Re-sort based on updated values
          sorted_list = sorted(sorted_list, key=lambda x: (this_account_etfs_dict[x]['delta_to_target']))
  #             check what the updated sorted list is
  #             for i in range(len(sorted_list)):
  #                 print(this_account_etfs_dict[sorted_list[i]]['symbol'] + ": " + str(round(this_account_etfs_dict[sorted_list[i]]['delta_to_target']*100,2)))
  #             print("\n")

          # Break for loop to restart and start from top of list again
          break


    return this_account_etfs_dict, money_remaining