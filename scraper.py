# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 19:03:34 2020

@author: Admin
"""

import requests
import pandas as pd
import simfin as sf
from simfin.names import *
from selenium import webdriver
from yahooquery import Ticker


#driver = webdriver.Chrome()

sf.set_api_key('free')

#download location
sf.set_data_dir('Z:\\SQA\\findata\\')


dff = sf.load_income(variant='quarterly', market='us')

# example for MICROSOFT
#print(dff.loc['AAPL', [REVENUE, NET_INCOME]])

#df_prices = sf.load_shareprices(market='us', variant='daily')

#df_prices.loc['AAPL', CLOSE].plot(grid=True, figsize=(20,10), title='AAPL Close')


df = pd.read_csv('nasdaqlisted.txt', names=["Symbol", "Security Name", "Market Category", "Test Issue", "Financial Status", "Round Lot Size", "ETF", "NextShares"], delimiter="|")
df[df.Symbol != 'File Creation']
print(df.head())  

'''
for i in df.index:
    a = df['Symbol'][i]
    driver.get('https://finance.yahoo.com/quote/'+a+'/key-statistics?p='+a)
    e = driver.find_element_by_link_text('Download')
    e.click()
'''
'''
for i in df.index:
     a = df["Symbol"][i]
     #print(a)
     if a == "PRN":
         a = "_PRN"
     res = requests.get('https://query1.finance.yahoo.com/v7/finance/download/' +a+'?period1=848275200&period2=1591747200&interval=1d&events=history')
     #print(res)
     open("Z:\\SQA\\nasdaq_data\\"+a+'.csv', 'wb').write(res.content)
'''

for i in df.index:
    name = str(df['Symbol'][i])
    print(name)
    try:
        tick = Ticker(name)
        tick.income_statement("q").to_csv(r'Z:\\SQA\\findata\\financials\\'+name+'_income.csv', index = False)
    except:
        print(name, "income doesn't work")
        open('Z:\\SQA\\findata\\financials\\missingData.txt', 'w').write(name+", income")
    try:
        tick = Ticker(name)
        tick.cash_flow("q").to_csv(r'Z:\\SQA\\findata\\financials\\'+name+'_cashFlow.csv', index = False)
    except:
        print(name, "cash flow doesn't work")
        open('Z:\\SQA\\findata\\financials\\missingData.txt', 'w').write(name+", cash flow")
    try:
        tick = Ticker(name)
        tick.balance_sheet("q").to_csv(r'Z:\\SQA\\findata\\financials\\'+name+'_balSheet.csv', index = False)
    except:
        print(name, "bal sheet doesn't work")
        open('Z:\\SQA\\findata\\financials\\missingData.txt', 'w').write(name+", balance sheet")
    try:
        tick = Ticker(name)
        keystats = pd.DataFrame.from_dict(tick.key_stats)
        keystats.to_csv(r'Z:\\SQA\\findata\\financials\\'+name+'_stats.csv', index = False)
    except:
        print(name, "statistics doesn't work")
        open('Z:\\SQA\\findata\\financials\\missingData.txt', 'w').write(name+", stats")
    #tick.login('leonz904@gmail.com', 'NNZT')
    
    
df2 = pd.read_csv('otherlisted.txt', names=["Symbol", "Security Name", "Market Category", "Test Issue", "Financial Status", "Round Lot Size", "ETF", "NextShares"], delimiter="|")
df2[df2.Symbol != 'File Creation']

'''
for i in df2.index:
     a = df2["Symbol"][i]
     #print(a)
     res = requests.get('https://query1.finance.yahoo.com/v7/finance/download/' +a+'?period1=848275200&period2=1591747200&interval=1d&events=history')
     #print(res)
     open("Z:\\SQA\\other_data\\"+a+'.csv', 'wb').write(res.content)
'''