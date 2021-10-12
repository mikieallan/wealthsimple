from helpers import wSimple
import pprint


DEBUG_MODE = False

if(DEBUG_MODE):
	tradeToken = "Bearer gAFS16IQEBCs-2Jim1sfLDI7jFYkHZjSubuttJ4W05k"

else:
	USE_ENV = str(input("\n\nDo you want to use preconfigured values (y/n)?\n>>> "))

	if USE_ENV == 'y':
		try:
			token = wSimple.login()
		except:
			print("An error occured, it's likely your trusted token expired. Please enter the OTP from Google Authenticator")
			otp = str(input("\n>>> "))
			token, otp_claim = wSimple.login(otp)
			print("\n\n\
				*****\n\n\
				TO MAKE LOGGING IN EASIER, ENTER THE BELOW TOKEN IN YOUR ENV FILE AS THE OTP CLAIM\
				\n\n" + otp_claim + "\n\n\
				*****\n\n")

	else:
		username = str(input("Enter username: \n>>> "))
		password = str(input("Enter password: \n>>> "))
		otp = str(input("Enter OTP: \n>>> "))
		token, otp_claim = wSimple.login(otp, username, password)
		print("\n\n\
			*****\n\n\
			TO MAKE LOGGING IN EASIER, ENTER THE BELOW TOKEN IN YOUR ENV FILE AS THE OTP CLAIM\
			\n\n" + otp_claim + "\n\n\
			*****\n\n")

	tradeToken = wSimple.switchToTrade(token)


### UNCOMMENT THE BELOW LINE TO GET THE TRADE TOKEN TO USE DEBUG MODE
#print(tradeToken)
###



# Set up variables, get account information
watchlist = wSimple.getWatchlist(tradeToken)
etfs = wSimple.getMyPresets()
etf_dict = wSimple.createEtfDict(watchlist, etfs)
my_holdings = wSimple.getAccountHoldings(tradeToken)

my_holdings = wSimple.getPositions(tradeToken, my_holdings)

if False:

	to_print = str(input("\n\nWhat do you want to see, totals or holdings?\n>>> ")).strip().upper()

	if to_print == "TOTALS":
		for key in my_holdings:
			print(my_holdings[key]['type'] + ": " + str(my_holdings[key]['total']))

	elif to_print == "HOLDINGS":
		pprint.pprint(my_holdings)

my_holding_keys = list(my_holdings.keys())

while (True):
	try:
		ch = 'A'
		print("\n\nWhich account would you like to transact in?\n")
		for key in my_holdings:
			print("  " + ch + ". " + my_holdings[key]['type'] + ", $" + str(my_holdings[key]['cash']['value']) + " available in cash")
			ch = chr(ord(ch) + 1)

		index = ord(input("\n>>> ").upper()) - 65

		account_of_interest = my_holding_keys[index]

		break

	except: 
		print("Invalid entry. Please choose a valid option from the list.")

		continue


etf_id_dict= wSimple.getCurrentPortfolioBalance(account_of_interest, etf_dict, my_holdings)


amount_to_contribute = int(input("\n\nAmount to use:\n>>> "))

while amount_to_contribute >= my_holdings[account_of_interest]['cash']['value']:
	print("You don't have enough cash to invest that much.\n")
	amount_to_contribute = int(input("Enter a valid amount to use:\n>>> "))

etfs_to_purchase, money_remaining = wSimple.getSharesToPurchase(my_holdings[my_holding_keys[0]], etf_id_dict, amount_to_contribute, True)


print("\n\nIf you want to use $" + str(amount_to_contribute) + ", you should purchase:\n")
for key in etfs_to_purchase:
	if (etf_id_dict[key]['to_buy'] != 0):
		print(etf_id_dict[key]['symbol'] + ": " + str(etf_id_dict[key]['to_buy']) + " at $" + str(etf_id_dict[key]['price']) + " for " + str(round(etf_id_dict[key]['to_buy'] * etf_id_dict[key]['price'],2)))

print("\nWhich will leave $" + str(round(money_remaining,2)) + " uninvested out of the $" + str(amount_to_contribute) + " total.")

to_purchase = input(str("\n\nDo you want to buy the above securities (y / n) in your "+ my_holdings[account_of_interest]['type'] + "?\n>>> ")).upper()

if (to_purchase == "Y"):
	print("\n")
	for key in etfs_to_purchase:
		if (etf_id_dict[key]['to_buy'] != 0):
			acc_id = account_of_interest
			sec_id = key
			quantity = etf_id_dict[key]['to_buy']
			price = etf_id_dict[key]['price']
			data = wSimple.buy(tradeToken, acc_id, sec_id, quantity, price)
			print(data['symbol'] + ": " + str(data['quantity']) + " purchased from " + data['account_id'])

else:
	print("\nNothing purchased\n")


