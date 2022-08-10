# file: scrape_details.py

from bs4 import BeautifulSoup
from urllib.request import urlopen
import datetime
import pdb
import os
from collections import namedtuple

JacksonFund = namedtuple('JacksonFund', [
                         'name', 'future_pct', 'actual_pct', 'num_units',
                         'unit_value', 'value', 'date'])

lookupId = dict({'JNL/Mellon Energy Sector': 190})
lookupId.update({'JNL/BlackRock® Global Natural Resources': 66})
lookupId.update({'JNL/Mellon Utilities Sector': 635})
lookupId.update({'JNL/Newton Equity Income': 606})
lookupId.update({'JNL/Invesco Diversified Dividend': 365})
lookupId.update({'JNL/Mellon Consumer Staples Sector': 368})
lookupId.update({'JNL/DFA U.S. Core Equity': 115})
lookupId.update({'JNL/Mellon Nasdaq® 100 Index': 222})

fundnames = ('JNL/BlackRock® Global Natural Resources',
             'JNL/Invesco Diversified Dividend',
             'JNL/Mellon Consumer Staples Sector',
             'JNL/Mellon Energy Sector',
             'JNL/Mellon Utilities Sector',
             'JNL/Newton Equity Income'
             'JNL/DFA U.S. Core Equity'
             'JNL/Mellon Nasdaq® 100 Index'
             )


class DetailsScraper:
    '''This class requires the source file to be scraped to be in the same 
    directory as the code, the current working directory'''

    def __init__(self):
        self.cwd = os.getcwd()
        file = input("Enter filename to be scraped:")
        self.url = f'file://{self.cwd}/{file}'
        self.ytdFile = f'{self.cwd}/detailsByDate.csv'
        self.funds = dict.fromkeys(fundnames, None)
        self.balances = dict()
        '''190  66 635 606  365 368 115 222'''

    def extract_fields(self, n, gc, dt):
        '''
        'name', 'future_pct', 'actual_pct', 'num_units','unit_value', 'value', 'date'])  # noqa: E501
        '''
    
        jf = JacksonFund(gc[n + 1].get_text(), gc[n + 3].get_text(),
                         gc[n + 2].get_text(), gc[n + 4].get_text().strip(),
                         gc[n + 5].get_text().strip(), gc[n + 6].get_text(), dt)  # noqa: E501
        return jf

    def save_to_csv(self, jf, file):
        record = f'{jf.name}, {jf.future_pct},{jf.actual_pct}, {jf.num_units},{jf.unit_value},{jf.value},{jf.date}\n'  # noqa: E501
        record.replace(' ', '')
        pdb.set_trace()
        file.write(record)

    def open_and_read(self):
        today = str(datetime.datetime.now())[0:10]
        page = urlopen(self.url)
        html = page.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')

        dta = soup.find(id="dialogForm:assetAllocation_dataTable_data")
        gcs = dta.find_all(role="gridcell")
        '''gcs: gridcells has 70 entries... so 10 accounts with 7 fields each.
        [1]= Name, [2]=actual% , [3] =future%,  [4]=numUnits,  [5]=unitValue, [6]=Value  # noqa: E501
        [8]= Name, [9]=actual% , [10]= future%, [11]= numUnits,[12]=unitVal,  [13]=Value 
        '''
        with open(self.ytdFile, "a") as ytdfile:
            headers = "name, future_pct, actual_pct, num_units,\
              unit_value, value, date\n".replace(' ', '')
            # ytdfile.write(headers)  just keep header in file.

            for i in range(0, 70, 7):
                jf = self.extract_fields(i, gcs, today)
                self.save_to_csv(jf, ytdfile)
