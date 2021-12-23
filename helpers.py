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
    for key in my_holdings:
      print(my_holdings[key]['type'] + ": " + str(my_holdings[key]['total']))
      for key2 in my_holdings[key]:
        if (type(my_holdings[key][key2]) == dict):
          if (key2 == "cash"):
            print("  Cash: " + str(my_holdings[key][key2]['value']))
          else:
            print("  " + my_holdings[key][key2]['symbol'] + ": " + str(my_holdings[key][key2]['value']) + ", Price: " + str(round(float(my_holdings[key][key2]['price']),2)))
    print("\n=====")

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
  def calculateCurrentPortfolioBalance(account, etf_dict, my_holdings):

    etf_id_dict = {}
    etf_id_list = [] # Mask for easy filtering, should improve
    total = 0

    # Populate dictionary with zeros for ETFs to account for ETFs that aren't currently held
    for key in etf_dict:
      etf_id_list.append(etf_dict[key]['id'])
      etf_id_dict[etf_dict[key]['id']] = {}
      etf_id_dict[etf_dict[key]['id']]['value'] = 0
      etf_id_dict[etf_dict[key]['id']]['price'] = float(etf_dict[key]['price'])
      etf_id_dict[etf_dict[key]['id']]['symbol'] = key
      etf_id_dict[etf_dict[key]['id']]['desired_weighting'] = ETF_LIST[key]

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
  def calculateSharesToPurchase(acct_holdings, etf_id_dict, amount_to_contribute, print_current):

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

    print_current = False
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
          
          # print("\n" + etf_id_dict[sorted_list[i]]['symbol'] + ": " + str(etf_id_dict[sorted_list[i]]['price']) + "\n")
          
          # update list of what to buy, money remaining, the current weighting, and the delta
          etf_id_dict[sorted_list[i]]['to_buy'] += 1
          money_remaining -= etf_id_dict[sorted_list[i]]['price']
          updated_value = etf_id_dict[sorted_list[i]]['price']+etf_id_dict[sorted_list[i]]['value']
          etf_id_dict[sorted_list[i]]['value'] = updated_value
          # update all current weightings and deltas
          for j in range(len(sorted_list)):
            etf_id_dict[sorted_list[j]]['current_ratio'] = etf_id_dict[sorted_list[j]]['value'] / total
            etf_id_dict[sorted_list[j]]['delta_to_target'] = (etf_id_dict[sorted_list[j]]['current_ratio'] - etf_id_dict[sorted_list[j]]['desired_weighting']) / etf_id_dict[sorted_list[j]]['desired_weighting']
          
          # Re-sort based on updated values
          sorted_list = sorted(sorted_list, key=lambda x: (etf_id_dict[x]['delta_to_target']))

          # Print values to double check
          # for i in range(len(sorted_list)):
          #  print(etf_id_dict[sorted_list[i]]['symbol'] + ": " + str(round(etf_id_dict[sorted_list[i]]['current_ratio'],3)) + ": " + str(round(etf_id_dict[sorted_list[i]]['desired_weighting'],3))  + ": " + str(round(etf_id_dict[sorted_list[i]]['value'],3)))
          # print("\n")
    
          break
    #pprint.pprint(etf_id_dict)
    return etf_id_dict, money_remaining
