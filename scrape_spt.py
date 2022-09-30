# file: scrape_spt.py
import os
from collections import namedtuple


data_dir = f'{os.getcwd()}/data'
csv_file = f'{data_dir}/detailsByDate.csv'
by_fund_file = f'{data_dir}/groupByfund.json'

FundInfo = namedtuple('FundInfo', ['fundId', 'invested', 'allocated'])


# used to get fundId, invested, allocated, given the fund name
lookupfund = dict()
lookupfund.update(
    {'JNL/MellonEnergySector': FundInfo(190, 9000, '15%')})
lookupfund.update(
    {'JNL/BlackRock®GlobalNaturalResources': FundInfo(66, 9000, '15%')})
lookupfund.update(
    {'JNL/MellonUtilitiesSector': FundInfo(635, 6000, '10%')})
lookupfund.update(
    {'JNL/NewtonEquityIncome': FundInfo(606, 6000, '10%')})
lookupfund.update(
    {'JNL/InvescoDiversifiedDividend': FundInfo(365, 9000, '15%')})
lookupfund.update(
    {'JNL/MellonConsumerStaplesSector': FundInfo(368, 6000, '10%')})
lookupfund.update(
    {'JNL/DFAU.S.CoreEquity': FundInfo(115, 6000, '10%')})
lookupfund.update(
    {'JNL/MellonNasdaq®100Index': FundInfo(222, 9000, '15%')})
lookupfund.update(
    {'JacksonFunds': FundInfo(-999, 60000, '100%')})

JacksonFund = namedtuple('JacksonFund',
                         ['fundId', 'name', 'invested', 'allocated',
                          'future_pct', 'actual_pct', 'num_units',
                          'unit_value', 'value', 'nvalue', 'date'])

GroupByFund = namedtuple('GroupByFund', ['fundId', 'invested', 'allocated',
                                         'percent', 'dates', 'values',
                                         'nvalues'])
