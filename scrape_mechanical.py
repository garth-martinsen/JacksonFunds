# file: scrape_mechanical.py

import re
import mechanicalsoup
import html
import urllib.parse
import pdb

browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
browser.open("http://jackson.com")
pdb.set_trace()


# browser.select_form('#signIn')
"""
Plan: Use mechanicalsoup to find and submit login username and password for:
Jackson.com, Then find and click the accountid to open the page with the 
account value ( eg: $60,000) and the jackson subaccounts. then scrape the
date, total account value, the subaccount data: fundId, allocation, name, 
value, etc. Write these out to the detailsByDate.csv file and to the 
groupByFund json file.

But: uopon opening the http://jackson.com page, I found that the HTML is 
hidden, I assume to prevent scraping.  It appears that this scheme will 
not work to do what I want it to do. See Plan above. 

Since the html is invisible to mechanicalsoup, I assume that Selenium
would do not better for the same reason. Until I learn more about how
to circumvent the invisible html, I see no reason to persue the Plan
above.


"""