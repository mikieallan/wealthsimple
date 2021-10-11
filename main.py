from helpers import wSimple
import pprint


DEBUG_MODE = True

if(DEBUG_MODE):
	tradeToken = "Bearer prOQqeZTfH5kKUhy0bjGL6HZhNuc_q6IW6Ei8LlbpJw"

else:
	USE_ENV = str(input("\n\nDo you want to use preconfigured values (y/n)?\n\n>>> "))

	if USE_ENV == 'y':
		try:
			token = wSimple.login()
		except:
			print("An error occured, it's likely your trusted token expired. Please enter the OTP from Google Authenticator")
			otp = str(input("\n\n>>> "))
			token, otp_claim = wSimple.login(otp)
			print("\n\n\
				*****\n\n\
				TO MAKE LOGGING IN EASIER, ENTER THE BELOW TOKEN IN YOUR ENV FILE AS THE OTP CLAIM\
				\n\n" + otp_claim + "\n\n\
				*****\n\n")

	else:
		username = str(input("Enter username: \n>>>"))
		password = str(input("Enter password: \n>>>"))
		otp = str(input("Enter OTP: \n>>>"))
		token, otp_claim = wSimple.login(otp, username, password)
		print("\n\n\
			*****\n\n\
			TO MAKE LOGGING IN EASIER, ENTER THE BELOW TOKEN IN YOUR ENV FILE AS THE OTP CLAIM\
			\n\n" + otp_claim + "\n\n\
			*****\n\n")

	tradeToken = wSimple.switchToTrade(token)

### UNCOMMENT THE BELOW LINE TO GET THE TRADE TOKEN TO USE DEBUG MODE
#print(tradeToken)

# Set up variables, get account information
watchlist = wSimple.getWatchlist(tradeToken)
etfs = wSimple.getMyPresets()
etf_dict = wSimple.createEtfDict(watchlist, etfs)
my_holdings = wSimple.getAccountHoldings(tradeToken)

my_holdings = wSimple.getPositions(tradeToken, my_holdings)

if False:

	to_print = str(input("\n\nWhat do you want to see, totals or holdings?\n\n>>> ")).strip().upper()

	if to_print == "TOTALS":
		for key in my_holdings:
			print(my_holdings[key]['type'] + ": " + str(my_holdings[key]['total']))

	elif to_print == "HOLDINGS":
		pprint.pprint(my_holdings)

ch = 'A'
print("\n\nWhich account would you like to transact in?\n")
for key in my_holdings:
	print(ch + ". " + my_holdings[key]['type'] + ", $" + str(my_holdings[key]['cash']['value']) + " available in cash")
	ch = chr(ord(ch) + 1)

index = ord(input("\n\n>>> ").upper()) - 65
my_holding_keys = list(my_holdings.keys())
etf_id_dict= wSimple.getCurrentPortfolioBalance(my_holding_keys[index], etf_dict, my_holdings)


amount_to_contribute = int(input("\n\nAmount to contribute:\n\n>>> "))
etfs_to_purchase = wSimple.getSharesToPurchase(my_holdings[my_holding_keys[0]], etf_id_dict, amount_to_contribute)


print("If you want to use $" + str(amount_to_contribute) + ", you should purchase:\n")
for key in etfs_to_purchase:
	if (etf_id_dict[key]['to_buy'] != 0):
		print(etf_id_dict[key]['symbol'] + ": " + str(etf_id_dict[key]['to_buy']) + " at $" + str(etf_id_dict[key]['price']))


