# JacksonFunds
The class in recover.py is RecoverJackson.It is supported by the configuration information in recover_spt.py. The class in scrape_jackson.py is ScrapeSavePlot supported by config information in scrape_spt.py. The spt files define paths and namedtuples used in the processing. root is the dir where the python code lives. RecoverJackson looks for its html input files in dir root/recover. ScrapeSavePlot looks for its html file inputs in main/data. The following will explain how to set up and process for RecoverJackson as I have run it.
Preparation to run the processes in RecoverJackson is: 
  a. open a browser and navigate to jackson.com
  b. log in with username and password.
  c. on the splash page, click the account number which opens the details page
  d. on the details page, set the datepicker to the desired date.
  e. click the link: Values. This opens a values dialog with two date columns to hold information of the subaccount on the desired date and yesterday's date.
  f. click in the matrix showing the subaccounts values to set focus.
  g. save the values page as mmmdd.html where mmmdd is the desired date, eg: sep30.html. always place a leading zero on dates less than 10 eg: sep01.html. This preserves the order when plotting the data.

Running RecoverJackson:
  a. in a terminal window start a python session by typing python, return
  b. type: from recover import RecoverJackson as RJ
  b. type: rj=RJ() # instanciates an instance of RJ class
  c. remove  csv file: rm detailsByDate.csv if scraping all of the html files, otherwise it will append to the existing file. 
  c. type: rj.scrape_many_html() to process a whole group of html files or rj.scrape_one_html() for a single file. You need to input file name using the scrape_one_html() version.
  d. When the scraping is done :
    rj.group_by_fund() will create a dictionary ({fundId: GroupFund}) as save it to disk as groupbyfund.json
    rj.plot_normalized() will call group_by_fund() , then plot X,Y family of plots with X=[dates] Y=[normalized_values]

  
  Figures follow: