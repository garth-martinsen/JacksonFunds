# JacksonFunds
The class in recover.py is RecoverJackson.It is supported by the configuration information in recover_spt.py. The class in scrape_jackson.py is ScrapeSavePlot supported by config information in scrape_spt.py. The spt files define paths and namedtuples used in the processing. RecoverJackson looks for its html input files in dir main/recover. ScrapeSavePlot looks for its html file inputs in main/data. 
Preparation to run the processes in RecoverJackson is: 
  a. open a browser and navigate to jackson.com
  b. log in with username and password.
  c. on the splash page, click the account number which opens the details page
  d. on the details page, set the datepicker to the desired date.
  e. click the link: Values. This opens a values dialog with two date columns to hold information of the subaccount on the desired date and yesterday's date.
  f. click in the matrix showing the subaccounts values to set focus.
  g. save the values page as mmmdd.html where mmmdd is the desired date, eg: sep30.html. always place a leading zero on dates less than 10 eg: sep01.html. This preserves the order when plotting the data.
  Figures follow:
  
