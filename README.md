# Wealthsimple
This project was built by inspecting network traffic on the Wealthsimple website to reverse engineer the API calls. 

The objective of this project is to automate the purchasing of a pre-defined portfolio and complete the auto-balancing. 

## Set up 
There are several user specific variables that need to be configured, including username, password, OTP_CLAIM, and the user's pre-defined portfolio. The OTP_CLAIM is a trusted token that allows the user to bypass the need for Google Authenticator for 30 days at a time. All of these should be done in an `config.py` file in this folder.

### User variables
* USERNAME = ""
* PASSWORD = ""
* OTP_CLAIM = ""

Example ETF_LIST
```json
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
```


*Important assumptions made in the development of this tool:* 
* The portfolio percentages are assumed to add up to 1, and are not verified
* All of the items in the ETF list will be in your watchlist
* The user has already purchased (no preventation logic has been put in for initial purchase, but it should work. However, has not be investigated as it's not relevant for me)

## Running

Once you have configured the appropriate variables, you can cd into this repoistory, run the below command, and follow the prompts.

```shell
python main.py
```