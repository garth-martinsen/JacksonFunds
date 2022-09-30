# recover.py

from bs4 import BeautifulSoup
from urllib.request import urlopen
import datetime
import pdb
import os
from collections import namedtuple
import csv
import recover_spt as spt
import json
import matplotlib.pyplot as plt
import re
import statistics


class RecoverJackson:
    '''
    This class can reconstruct values at past dates whereas scrape_jackson can 
    only capture todays values.  Process:
    1. Capture the html file of the values page 
        a. login to jackson.com
        b. click on the account number link
        c. located the date and click on the date picker.
        d. select the date desired eg: sep 09, 2022 if today is after that.
        e. click the Values link. This opens the values page.
        f. save the page as html to disk for later analysis. name =mmmdd.html
        where mmm is 3 letter name of month eg: mar or sep or oct, etc.
    Each html file will have two data sets, one for the selected date and 
    one for todays date.
    This class scrapes only the info for the selected date and ignores today's 
    date. By doing this for each day desired, one can see the timeline from 
    the earliest html file until the latest. One must take care to name files 
    with a preceding zero for days less than 10 to preserve order in the plot. 
    eg: sep01.html, sep09.html, etc.
    1. If user calls scrape_many_html(), All existing html files are 
    scraped in date order.
    Once the csv file, detailsByDate.csv holds all of the data: 
    2. if user calls method group_by_fund() a dictionary. {fundId, GroupFund} 
    of GroupFund records, each having the fundId, name, invested, allocated, 
    list[dates], list [values], list [nvalues], where nvalues are: (each value 
    normalized by the invested amount, resulting in values around 1.0.) 
    3. If user calls plot_normalized()... group_by fund is called and A plot 
    is presented with a timeline for each Jackson subaccount. This is a family 
    of curves.  A reference line is plotted at y=1.0. 
    All subaccount nvalues above the line have grown above the investment 
    amount.(money has been earned ). When the time line drops below the 
    reference line, money has been lost compared to what was invested.
    Due to the nature of the stock market, a subaccount will cross the
    reference line many times as prices drop or grow.

    '''


    def __init__(self):
        '''
        set paths and files on self from the spt file imported.
        '''
        self.csv_file = spt.csv_file
        self.data_dir = spt.data_dir
        self.recover_dir = spt.recover_dir
        self.lookupfund = spt.lookupfund
        self.by_fund_file = spt.by_fund_file

    def isodate(self, date):
        '''
        jackson formats dates as mm/dd/yyyy eg: 08/18/2022
        iso formats dates as yyyy-mm-dd eg: 2022-18-08
        All dates in this class will be formatted for iso.
        This function will convert jackson to iso format.
        If date is already iso formatted, it is returned.
        '''
        if '/' in date:
            mdy = date.split('/')
            iso = f'{mdy[2]}-{mdy[0]}-{mdy[1]}'
            return iso
        else:
            return date

    def extract_fields(self, idx, tds, date):
        '''
        tds is the collection of <td> tags, and has a len of 70.
        0:name, 1:num_units, 2: unit_value, 3: tot_value, 4:
        from spt.JacksonFund:
        ['fundId', 'name', 'invested', 'allocated', 'future_pct', 'actual_pct',
         'num_units', 'unit_value', 'value', 'nvalue', 'date'])
        '''

        # pdb.set_trace()

        name = tds[idx].get_text().replace(' ', '')
        fundInfo = self.lookupfund.get(name, None)
        if fundInfo is not None:
            print(f'idx: {idx}  {name}')
            num_units = float(tds[idx + 1].get_text().replace(',', ''))
            unit_value = float(tds[idx + 2].get_text().replace(',', ''))
            value = float(tds[idx + 3].get_text()[1:].replace(',', ''))
            fundid = fundInfo.fundId
            invested = fundInfo.invested
            allocated = fundInfo.allocated
            future_pct = allocated
            act_pct = f'{round(value / 60000*100)}%'
            nvalue = round(value / invested, 3)
            jf = spt.JacksonFund(fundid, name, invested, allocated, future_pct,
                                 act_pct, num_units, unit_value, value,
                                 nvalue, date)
            self.save_to_csv(jf)

    def save_to_csv(self, jf):
        '''
        convert jf to string with newline at end, open and append string to 
        csv_data file 
        '''
        record = f'{jf.fundId},{jf.name}, {jf.invested},\
                    {jf.future_pct}, {jf.actual_pct}, {jf.num_units},\
                    {jf.unit_value}, {jf.value}, {jf.nvalue}, \
                    {jf.date}\n'

        record = record.replace(' ', '')

        with open(self.csv_file, 'a') as csv_data:
            # pdb.set_trace()
            csv_data.write(record)

    def open_and_read(self, file):
        '''
        file is an html file to be scraped.
        Use beautiful soup to scrape info from page
        All dates will be expressed as isodates eg: '2022-08-19'
        '''
        url = f'file://{self.recover_dir}/{file}'
        page = urlopen(url)
        html = page.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html5lib')  # 'html.parser'

        tbls = soup.find_all('table')
        tbl = tbls[5]
        ths = tbl.find_all('th')
        # for recover, do not need current date, d2, nor current value, v2
        dt = self.isodate(ths[1].get_text()[11:].strip())
        print(dt)

        # pdb.set_trace()

        tbds = soup.find_all('tbody')
        tds = tbds[5].find_all('td')

        value = round(
            float(tds[1].get_text().strip()[1:].replace(',', '')), 3)
        fundInfo = self.lookupfund['JacksonFunds']
        invested = fundInfo.invested
        nv = round(value / invested, 3)  # normalized value
        act_pct = f'{round(nv*100)}%'
        num_units = 81  # summed over all subaccounts by Garth
        unit_value = round(value / 81, 3)
        # build and save the overall csv record
        # pdb.set_trace()

        jf = spt.JacksonFund(-999, 'JacksonFunds', invested, '100%', '100%',
                             act_pct, num_units, unit_value,
                             value, nv, dt)
        self.save_to_csv(jf)
        # iterate thru files to build and save the subaccounts
        sats = soup.find(id="dialogForm:valueAsOfSubaccountTable")
        tds = sats.find_all('td')
        i = 0
        # pdb.set_trace()
        for t in tds:
            self.extract_fields(i, tds, dt)
            if i < 56:
                i = i + 7
                print(f'idx is: {i}')

    def scrape_one_html(self):

        file = input("scrape file: ")
        self.open_and_read(file)

    def scrape_many_html(self):
        '''
        Iterates thru all html files in data_dir, scrapes data and
        appends to output file: detailsByDate.csv. After last file,
        closes file detailsByDate.csv. It is important to use 2 digits
        for the day, for all days under 10, with a leading zero, to
        keep the dates in order in the csv file for use in later plots.
        '''
        os.chdir(self.recover_dir)
        files = os.listdir()
        hfiles = []
        # filter so only html files are collected
        [hfiles.append(f) for f in files if f.endswith('html')]
        hfiles.sort()

        for hf in hfiles:
            self.open_and_read(hf)

    def group_by_fund(self):
        '''
        Opens, reads all entries in csv file: detailsByDate.csv 
        collects all fundid, allocation, dates and amounts into a
        namedtuple: GroupByFund, which has fundId, invested,
        allocation, list[dates], list[Amounts], list[normalized_amts].
        The lists are associated so dates[0] corresponds to: values[0]
        GroupByFund = namedtuple('GroupByFund', ['fundId', 'invested',
        'percent', 'dates', 'values', nvalues]) 
        JacksonFund = namedtuple('JacksonFund',
        ['fundId', 'name', 'invested', 'future_pct','actual_pct', 'num_units', 'unit_value', 'value', 'date']) eg:# noqa: E501
        csv: 66,JNL/BlackRock®GlobalNaturalResources,9000,15.00%,14.40%,738.3417,11.544138,8523.52,2022-09-02  # noqa: E501
        '''
        # Avoid filling the dates and values with more than one set by new dict
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
        Best performers will be listed first.
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
