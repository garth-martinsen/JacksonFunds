# file: experimental.py


from bs4 import BeautifulSoup
from urllib.request import urlopen
import datetime
import pdb
import os
from collections import namedtuple
import csv
import scrape_spt as spt
import json
import matplotlib.pyplot as plt
import re
import statistics


class ScrapeSavePlot:
    '''
    1.First, Save html from http://jackson.com page for my account details.
    It is required to login with username and password, then pass 2nd
    level authentication, then click on account number to open
    details page to be scraped. Command-s saves the html.
    Html files are saved to disk in cwd/data eg: data/aug21.html

    2. Scraping of html file will produce data to create namedtuple,
    JacksonFund, in which dates will be in iso format: yyyy-mm-dd
    The JacksonFund from each page is appended to detailsByDate.csv
    file.
    3. user calls group_by_fund() and the dictionary groupByFund is updated
    with the latest JacksonFund data, and is saved to groupByfund.json.  
    4. Plotting is done against the data
    in the groupByFund dictionary, where [X]= dates, [Y]=nvalues
    for each fundId. where nvalues is The JacksonFund.value normalized by
    JacksonFund.invested field, yielding a number close to 1.0
    '''

    def __init__(self):
        '''
        constructor: makes files and lookups accessible from self
        '''
        self.data_dir = spt.data_dir
        self.csv_file = spt.csv_file
        self.by_fund_file = spt.by_fund_file
        self.lookupfund = spt.lookupfund
        self.groupbyfund = dict()  # {fundId: GroupByFund(...)}

    def scrape_one_html(self):
        '''
        Prompts for input html file to scrape, scrapes data and appends
        to detailsByDate.csv, and closes csv_file.
        '''
        file = input('Enter file name to scrape:')
        self.open_and_read(file)

    def scrape_all_html(self):
        '''
        Iterates thru all html files in data_dir, scrapes data and
        appends to output file: detailsByDate.csv. After last file,
        closes file detailsByDate.csv. It is important to use 2 digits
        for the day, for all days under 10, with a leading zero, to 
        keep the dates in order in the csv file for use in later plots. 
        '''
        os.chdir(self.data_dir)
        files = os.listdir()
        hfiles = []
        # filter so only html files are collected
        [hfiles.append(f) for f in files if f.endswith('html')]
        hfiles.sort()
        for hf in hfiles:
            self.open_and_read(hf)

    def get_date_and_total_balance(self, soup, file):
        '''
        Find the date and total amount in Jackson, and write it
        as a JacksonFund(...) in csv file. All Dates will be in
        iso format: eg: '2022-08-17'
        eg:JacksonFund(fundId, name, invested, future_pct,
                       actual_pct, num_units, unit_value,
                      value, date])
        '''
        # pdb.set_trace()

        dt = soup.find(id="policyDetailsForm:valueAsOfDate_input")
        date = self.isodate(str(dt)[-13:-3])
        acc = soup.find(id='policyDetailsForm:addlDetailsPanel')
        # apr 26, 2022 invested $60,000 in Jackson.
        # create list of amounts: Deposited, DeathBenefit, Accum, CashSurrender
        values = re.findall("\d{2},\d{3}.\d{2}", acc.get_text())

        invested = float(values[0].replace(',', ''))
        accum = float(values[2].replace(',', ''))
        normalized = round(accum / invested, 3)
        # sum of num_units over all of the sub accounts = 2769.
        unit_value = round(invested / 2769, 3)
        pct = round(100 * normalized, 2)
        record = f'-999, JacksonFunds, {invested},  {100}%, {pct}%, {2769}, \
        {unit_value}, {accum}, {normalized}, {date}\n'
        record = record.replace(' ', '')
        # print(record)
        file.write(record)
        return (date, accum)

    def extract_fields(self, n, gc, dt):
        '''
        Build and return a JacksonFund namedtuple from the gridcell values, 
        gc, and the fundInfo from lookup dict, lookupfund. ({name: FundInfo}).
        '''
        name = gc[n + 1].get_text()

        fundInfo = self.lookupfund.get(name.replace(' ', ''), None)
        # print(name, fundInfo)
        if fundInfo is not None:
            # pdb.set_trace()
            fundId = fundInfo.fundId
            invested = fundInfo.invested
            allocated = fundInfo.allocated
            future_pct = gc[n + 3].get_text()
            actual_pct = gc[n + 2].get_text()
            num_units = float(gc[n + 4].get_text())
            unit_value = float(gc[n + 5].get_text())
            value = float(gc[n + 6].get_text().replace(',', '')[1:])
            nvalue = round(value / invested, 3)
            date = self.isodate(dt)
            # pdb.set_trace()
            jf = spt.JacksonFund(fundId, name, invested, allocated,
                                 future_pct, actual_pct, num_units,
                                 unit_value, value, nvalue, date)  # noqa: E501
            return jf

    def open_and_read(self, file):
        '''
        file is an html file to be scraped.
        Use beautiful soup to scrape info from page
        All dates are expressed as isodates eg: '2022-08-19'
        '''
        self.url = f'file://{self.data_dir}/{file}'
        page = urlopen(self.url)
        html = page.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html5lib')  # 'html.parser'

        '''gcs: gridcells has 70 entries... so 10 accounts with 7 fields each. 7th field is ignored
        [1]= Name, [2]=actual% , [3] =future%,  [4]=numUnits,  [5]=unitValue, [6]=Value  # noqa: E501
        [8]= Name, [9]=actual% , [10]= future%, [11]= numUnits,[12]=unitVal,  [13]=Value 
        '''
        with open(self.csv_file, "a") as csv_file:
            headers = "name, invested, future_pct, actual_pct, num_units,\
              unit_value, value, date\n".replace(' ', '')
            # csv_file.write(headers)  just keep header in file.
            # first save total balance and date as first jf.
            date, accum = self.get_date_and_total_balance(soup, csv_file)

            # then iterate thru the subaccounts and get a jf for each...
            dta = soup.find(id="dialogForm:assetAllocation_dataTable_data")
            gcs = dta.find_all(role="gridcell")
            for i in range(0, 70, 7):
                jf = self.extract_fields(i, gcs, date)
                '''
                 eg:JacksonFund(fundId, name, invested, future_pct,
                       actual_pct, num_units, unit_value,
                      value, date])
                '''
                if jf is not None:
                    record = f'{jf.fundId},{jf.name}, {jf.invested},\
                    {jf.future_pct}, {jf.actual_pct}, {jf.num_units},\
                    {jf.unit_value}, {jf.value}, {jf.nvalue}, \
                    {jf.date}\n'
                    record = record.replace(' ', '')
                    csv_file.write(record)

    def isodate(self, date):
        '''
        jackson formats dates as mm/dd/yyyy eg: 08/18/2022
        iso formats dates as yyyy-mm-dd eg: 2022-18-08
        this function will convert jackson to iso format.
        All dates in this python script will be formatted for iso.
        If date is already iso formatted, just return it.
        '''
        if '/' in date:
            mdy = date.split('/')
            iso = f'{mdy[2]}-{mdy[0]}-{mdy[1]}'
            return iso
        else:
            return date

    def group_by_fund(self):
        '''
        Opens, reads all entries in csv file: detailsByDate.csv 
        collects all fundid, allocation, dates and amounts into a
        namedtuple: GroupByFund, which has fundId, invested,
        allocation, list[dates], list[Amounts].
        The lists are associated so dates[0] corresponds to: values[0]
        GroupByFund = namedtuple('GroupByFund', ['fundId', 'invested',
                                         'percent', 'dates', 'values'])
        JacksonFund = namedtuple('JacksonFund',
         ['fundId', 'name', 'invested', 'future_pct','actual_pct', 'num_units', 'unit_value', 'value', 'date'])
        csv: 66,JNL/BlackRock®GlobalNaturalResources,9000,15.00%,14.40%,738.3417,11.544138,8523.52,2022-09-02  # noqa: E501
        '''
        # Avoid filling the dates and values with more than one set.
        self.groupbyfund = dict()
        with open(self.csv_file, 'r') as file:
            reader = csv.reader(file)
            # reader.__next__()     # uncomment to waste header
            # pdb.set_trace()
            for row in reader:
                print(row)
                fid = int(row[0])
                nm = row[1]
                iv = float(row[2])
                fpct = row[3]
                apct = row[4]
                nu = float(row[5])
                uv = float(row[6])
                val = float(row[7])
                # pdb.set_trace()
                # invested = self.lookupfund[nm.replace(' ', '')].invested
                nval = round(val / iv, 3)
                dt = self.isodate(row[9])

                jf = spt.JacksonFund(fid, nm, iv, fpct, fpct, apct, nu, uv, val, nval, dt)  # noqa: E501

                gbf = self.groupbyfund.get(jf.fundId,
                                           spt.GroupByFund(jf.fundId,
                                                           jf.invested,
                                                           jf.allocated,
                                                           jf.actual_pct,
                                                           [], [], []))

                gbf.dates.append(jf.date)
                gbf.values.append(float(jf.value))
                gbf.nvalues.append(jf.nvalue)
                self.groupbyfund.update({gbf.fundId: gbf})

            # after all csv rows, save the updated dictionary
            self.save_group_by_fund()

    def save_group_by_fund(self):
        '''
        Writes the contents of self.group_by_fund to disk as json file.
        '''
        with open(self.by_fund_file, 'w') as json_file:
            json_file.write(json.dumps(self.groupbyfund) + '\n')
        print("groupbyfund dictionary is saved to disk...")

    def rank_funds(self):
        '''
        For each account, Averages all normalized values and creates
        tuple (name, avg), which is appended to a list, performances. 
        Sorts the performances in reverse order and prints them out
        The highest performers will be listed first.
        '''
        performances = list()
        self.group_by_fund()
        for k, v in self.groupbyfund.items():
            actnm = f'jf{k}'
            avg = round(sum(v.nvalues) / len(v.nvalues), 3)
            # pdb.set_trace()
            sd = round(statistics.stdev(v.nvalues, avg), 3)
            performances.append((actnm, avg, sd))

        performances.sort(reverse=True, key=lambda element: element[1])
        print(' Jackson Subaccounts Ranked by average ROI Performance:')
        print(f' account  mean  stdDeviation')
        for t in performances:
            print(f' {t[0]} : {t[1]} - {t[2]}')

    def plot_normalized(self):
        '''
        Uses matplotlib.plt, dict, self.lookupfund and dict, self.groupbyfund,
        to plot normalized account value over time. 
        a GroupByFund from dict, self.groupbyfund, holds dates and normalized 
        values as lists which will yield X[] and Y[] needed for plt.
        '''
        # load the groupbyfund dict using the csv file.
        self.group_by_fund()

        # now plot the data
        fig, ax = plt.subplots(constrained_layout=True)
        plt.ylabel('normalized $')
        # pdb.set_trace()
        # xlbl = f'{spt.MONTH[mm]}_{spt.YEAR}'
        plt.xlabel('Date')
        # pdb.set_trace()

        plt.title('Jackson Fund performance, normalized')
        X = []  # days
        Y = []  # normalized values
        end = 0
        for k, v in self.groupbyfund.items():
            Y.clear()
            X.clear()
            [Y.append(nv) for nv in v.nvalues]
            # just need dd and mm from isodate. Only collect dates in month mm.
            [X.append(d[-5:]) for d in v.dates]
            lbl = f'{k}'
            # pdb.set_trace()
            pct = f'{k}-{round(v.nvalues[-1]*100,2)}%'
            plt.setp(ax.get_xticklabels(), rotation=70, ha="right")
            # make the Jackson overall plot stand out.
            plt.annotate(lbl, (X[0], Y[0]))
            plt.annotate(pct, (X[-1], Y[-1]))
            if k == -999:

                plt.plot(X, Y, "ro-", ms=4,
                         markevery=1, label=lbl)
            else:
                plt.plot(X, Y, label=lbl)
                end = len(X)
        # break-even line should span the dates...

        plt.plot([0, end], [1.0, 1.0], "k-", label="Break-Even")
        # plt.legend()
        plt.show()
