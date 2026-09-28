# 1 GET /AccountDetails Account details
    Not working for manaher account,
        {
        "retcode": 0,
        "id": "1",
        "login": 100025,
        "name": "Demo Client Account",
        "group": "demo\\Standard",
        "currency": "USD",
        "balance": "10000.00",
        "equity": "10000.00",
        "margin": "0.00",
        "margin_free": "10000.00",
        "margin_level": "999999",
        "leverage": 100,
        "enabled": true
        }
    Showing this respose for manager account 1000, and not available accounts in DB.
    And why does this alwas show "margin_level": "999999", for all accounts?

# 2 GET /Accounts Account numbers
        {
        "retcode": 0,
        "message": "Success",
        "endpoint": "/Accounts",
        "data": []
        }


# 3 GET /AccountsSummary Accounts Balance, Equity,Profit, etc
        {
        "retcode": 0,
        "message": "Success",
        "endpoint": "/AccountsSummary",
        "data": []
        }

