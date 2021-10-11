### User variables
USERNAME = ""
PASSWORD = ""
OTP_CLAIM = ""

ETF_LIST = {
    "VUN": 0.175, 
    "VVO": 0.075, 
    "XEF": 0.175, 
    "XIC": 0.10, 
    "XUT": 0.025, 
    "ZAG": 0.075, 
    "ZHY": 0.075, 
    "ZLE": 0.125, 
    "ZQQ": 0.15, 
    "ZRE": 0.025
}

### Configs
# Base URLs
BASE_URL = "https://api.production.wealthsimple.com"
TRADE_BASE_URL = "https://trade-service.wealthsimple.com"

#Misc
CLIENT_ID = "4da53ac2b03225bed1550eba8e4611e086c7b905a3855e6ed12ea08c246758fa"
SCOPES = "invest.read invest.write mfda.read mfda.write mercer.read mercer.write trade.read trade.write empower.read empower.write tax.read tax.write"
TRADE_CLIENT_ID = "qTgfOYKjgj_qOFKyo-AgMauB_GzywmKXoPUUDS4rF04"


## Endpoints
LOGIN_ENDPOINT = "/v1/oauth/token"
SWITCH_ENDPOINT = "/v1/oauth/switch"
POSITIONS_ENDPOINT = "/account/positions"
WATCHLIST_ENDPOINT = "/watchlist"
ACCOUNT_LIST_ENDPOINT = "/account/list"