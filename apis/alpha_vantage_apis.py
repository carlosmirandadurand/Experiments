#%% #######################################################################################################
# Alpha Vantage API
# Financial Data for Applications 
#
# Contents
#  - Realtime & historical stock market data 
#  - Forex, commodity & crypto data 
#  - technical & economic indicators
#  - Market news & sentiments
#
# Sources:
# - https://www.alphavantage.co/
# - API definitions: https://www.alphavantage.co/documentation/
#
###########################################################################################################

import os
import time
import pandas as pd
import numpy as np
import requests

from dotenv import load_dotenv
from datetime import datetime

import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas


#%% #######################################################################################################
# Set process parameters 
###########################################################################################################

load_dotenv()

# Process attributes
time_stamp = datetime.today().strftime('%Y-%m-%d')

# Snowflake input parameters
alpha_vantage_access_key    = os.getenv('alpha_vantage_access_key')

# Check parameters
print(f'Timestamp: {time_stamp}')


# Ticker lists
transp_list = ['FDX','UPS','DPW.DE','UNP','MAERSK.B',]  #'AMKBY'  (research missing stocks)
tech_list   = ["MSFT", "AAPL", "AMZN", "NVDA", "GOOG", "GOOGL", "IBM", "META", "INTC", "CSCO"]
bank_list   = ['BAC','JPM','WFC','TFC','RF','RY','C','COF','HSBC','MS',]
bank_list2  =['FRCB','SBNY','SIVB','AMSB','FCBF','TFSB','EBSB','CNJB','RSIB','LCNB','ESBK','WFB','FMS','FABK','GTBK','FNB','PFBC','SEBC','HCBN','ALBK','WBCO','FCNK','TCB','NMSB','HTNB','TBOG','PBNK','EBDK','DBNK','CCBT','HCBK',]
print(len(transp_list))
print(len(tech_list))
print(len(bank_list))
print(len(bank_list2))



#%% #######################################################################################################
# Helper Function to access API
###########################################################################################################

def get_alpha_vantage_single_time_series (
        symbol, 
        api_key, 
        function = 'TIME_SERIES_DAILY_ADJUSTED', 
        time_series_name = 'Time Series (Daily)'
        ):
    
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": {function}, 
        "symbol": symbol,
        "apikey": api_key,
        "datatype": "json",
        "outputsize": "full" 
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        time_series_data = data.get(time_series_name, {}) 
        df = pd.DataFrame.from_dict(time_series_data, orient='index')
        df.index = pd.to_datetime(df.index)
        for column in df.columns:
            df[column] = df[column].astype(float)
        df.columns = df.columns.str.replace(' ', '_', regex=True)
        df.columns = df.columns.str.replace(r'\d+._', '', regex=True)            
        df['symbol'] = symbol
        return df
    else:
        return pd.DataFrame()  


def get_alpha_vantage_time_series (
        symbols, 
        api_key, 
        function = 'TIME_SERIES_DAILY_ADJUSTED', 
        time_series_name = 'Time Series (Daily)'
        ):
    
    df_list = [] 
    for symbol in symbols:
        df = get_alpha_vantage_single_time_series(symbol, api_key, function, time_series_name)
        df_list.append(df)
        print(f'Pulled {symbol}...')
        time.sleep(12)  # add a delay of 12 seconds

    result = pd.concat(df_list)
    return result


def check_time_series (df):
    grouped_data = df.groupby('symbol')
    results = grouped_data.agg({
        'adjusted_close': ['min', 'max'],
        'volume': 'sum',
    })
    results['number_of_days_traded'] = grouped_data.size()
    results['first_date'] = grouped_data.apply(lambda x: x.index.min())
    results['last_date'] = grouped_data.apply(lambda x: x.index.max())
    results.columns = ['min_adjusted_close', 'max_adjusted_close', 'total_volume', 'number_of_days_traded', 'first_date', 'last_date']
    return results


def get_alpha_vantage_single_financial_statement (
        symbol, 
        api_key, 
        function = 'BALANCE_SHEET', 
        report_name = 'annualReports'
        ):
    
    base_url = "https://www.alphavantage.co/query"
    params = {
        "function": function, 
        "symbol": symbol,
        "apikey": api_key,
        "datatype": "json",
    }
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        annual_reports = data.get(report_name, [])
        df = pd.DataFrame(annual_reports)   
        df = df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
        df.columns = df.columns.str.replace(' ', '_', regex=True)
        df.columns = df.columns.str.replace(r'\d+._', '', regex=True) 
        df['symbol'] = symbol
        return df
    else:
        return pd.DataFrame() 


def get_alpha_vantage_financial_statement (
        symbols, 
        api_key, 
        function = 'BALANCE_SHEET', 
        report_name = 'annualReports'
        ):
    df_list = [] 
    for symbol in symbols:
        df = get_alpha_vantage_single_financial_statement(symbol, api_key, function, report_name)
        if not df.empty:
            df_list.append(df)

    result = pd.concat(df_list, ignore_index=True, sort=False)
    return result


def check_balance_sheet (df):
    grouped_data = df.groupby('symbol')
    results = grouped_data.agg({
        'fiscalDateEnding': ['min', 'max'],
        'totalAssets': ['min', 'max'],
        'retainedEarnings': 'sum',
    })
    results['records'] = grouped_data.size()
    results.columns = ['first_date', 'last_date', 'min_total_assets', 'max_total_assets', 'total_retained_earnings', 'records']
    return results


def check_income_statement (df):
    grouped_data = df.groupby('symbol')
    results = grouped_data.agg({
        'fiscalDateEnding': ['min', 'max'],
        'totalRevenue': ['min', 'max'],
        'netIncome': 'sum',
    })
    results['records'] = grouped_data.size()
    results.columns = ['first_date', 'last_date', 'min_total_revenue', 'max_total_revenue', 'total_net_income', 'records']
    return results


def check_cash_flow (df):
    grouped_data = df.groupby('symbol')
    results = grouped_data.agg({
        'fiscalDateEnding': ['min', 'max'],
        'operatingCashflow': ['min', 'max'],
        'netIncome': 'sum',
    })
    results['records'] = grouped_data.size()
    results.columns = ['first_date', 'last_date', 'min_operating_cash_flow', 'max_operating_cash_flow', 'total_net_income', 'records']
    return results



def print_json(obj, indent=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (list, dict)):
                print(f"{indent}{k}: {type(v).__name__}")
                print_json(v, indent + '\t')
            else:
                print(f"{indent}{k}: {v}")
    elif isinstance(obj, list):
        for i in range(len(obj)):
            if isinstance(obj[i], (list, dict)):
                print(f"{indent}[{i}]: {type(obj[i]).__name__}")
                print_json(obj[i], indent + '\t')
            else:
                print(f"{indent}[{i}]: {obj[i]}")



#%% #######################################################################################################
# Execute
###########################################################################################################


# data = get_alpha_vantage_time_series (['BAC'], alpha_vantage_access_key)
# data = get_alpha_vantage_financial_statement (['BAC'], alpha_vantage_access_key, 'BALANCE_SHEET')
# data = get_alpha_vantage_financial_statement (['BAC'], alpha_vantage_access_key, 'INCOME_STATEMENT')
# data = get_alpha_vantage_financial_statement (['BAC'], alpha_vantage_access_key, 'CASH_FLOW')
data = get_alpha_vantage_financial_statement (['BAC'], alpha_vantage_access_key, 'EARNINGS', 'annualEarnings')
data



#%% #######################################################################################################
# EDA & Tests 
###########################################################################################################

# #----- Explore Data -----
# # Exploring contents from TIME_SERIES_DAILY_ADJUSTED function
# url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=BAC&outputsize=full&apikey={alpha_vantage_access_key}'
# r = requests.get(url)
# data = r.json()
# print_json(data)

# # Exploring contents from BALANCE_SHEET function
# url = f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol=BAC&apikey={alpha_vantage_access_key}'
# r = requests.get(url)
# data = r.json()
# print_json(data)

# # Exploring contents from EARNINGS function
# url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol=BAC&apikey={alpha_vantage_access_key}'
# r = requests.get(url)
# data = r.json()
# print_json(data)

# # Exploring contents from EARNINGS_CALENDAR function
# url = f'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol=BAC&horizon=12month&apikey={alpha_vantage_access_key}'  # Fix issue!
# r = requests.get(url)
# data = r.json()
# print_json(data)

# # Exploring contents from INFLATION function
# url = f'https://www.alphavantage.co/query?function=INFLATION&apikey={alpha_vantage_access_key}'
# r = requests.get(url)
# data = r.json()
# print_json(data)

# # Exploring contents from SMA function (simple moving average)
# url = f'https://www.alphavantage.co/query?function=SMA&symbol=USDEUR&interval=weekly&time_period=10&series_type=open&apikey={alpha_vantage_access_key}'
# r = requests.get(url)
# data = r.json()
# print_json(data)



# #----- Testing simple functions -----
# data = get_alpha_vantage_single_time_series("MSFT", alpha_vantage_access_key)
# print(data.head())

# data = get_alpha_vantage_single_financial_statement("MSFT", alpha_vantage_access_key)
# print(data)



# #----- Testing multi-ticker functions -----
# data = get_alpha_vantage_time_series(bank_list2, alpha_vantage_access_key)
# summary_data = check_time_series(data)
# print(data.shape)
# print(data.head())
# print(summary_data.shape)
# print(summary_data)

# data = get_alpha_vantage_financial_statement(transp_list, alpha_vantage_access_key)
# summary_data = check_balance_sheet(data)
# print(data.shape)
# print(data.head())
# print(summary_data.shape)
# print(summary_data)

# data = get_alpha_vantage_financial_statement(transp_list, alpha_vantage_access_key, 'INCOME_STATEMENT')
# summary_data = check_income_statement(data)
# print(data.shape)
# print(data.head())
# print(summary_data.shape)
# print(summary_data)

# data = get_alpha_vantage_financial_statement(transp_list, alpha_vantage_access_key, 'CASH_FLOW')
# summary_data = check_cash_flow(data)
# print(data.shape)
# print(data.head())
# print(summary_data.shape)
# print(summary_data)



#%% #######################################################################################################
# Lists for Reference
###########################################################################################################

# Transportation
#    FedEx Corporation:                                                                                                                                               FDX
#    United Parcel Service, Inc. (UPS):                                                                                                                               UPS
#    DHL is a division of the German logistics company Deutsche Post DHL Group, which is publicly traded in Germany:                                                  DPW.DE
#    Union Pacific Corporation (a major railroad company in the U.S.):                                                                                                UNP
#    Maersk (officially known as A.P. Moller - Maersk A/S, a Danish international shipping company): AMKBY (U.S. OTC markets) or MAERSK.B (Copenhagen Stock Exchange) AMKBY  MAERSK.B 

# Large banks:
#    Bank of America Corporation:                                                   BAC
#    JPMorgan Chase & Co. (Chase Bank):                                             JPM
#    Wells Fargo & Company:                                                         WFC
#    Truist Financial Corporation (Formed by the merger of BB&T and SunTrust Bank): TFC
#    Regions Financial Corporation (Regions Bank):                                  RF
#    Royal Bank of Canada:                                                          RY
#    Citybank:                                                                      C
#    Capital One Financial :                                                        COF
#    HSBC:                                                                          HSBC
#    Morgan Stanley:                                                                MS
#
# Failed banks (2015-2023/07):
#    First Republic Bank	                            FRCB (delisted)
#    Signature Bank	                                    SBNY
#    Silicon Valley Bank	                            SIVB (delisted)
#    Almena State Bank	                                AMSB (delisted)
#    First City Bank of Florida	                        FCBF (delisted)
#    The First State Bank	                            TFSB (delisted)
#    Ericson State Bank	                                EBSB (delisted)
#    City National Bank of New Jersey	                CNJB
#    Resolute Bank	                                    RSIB
#    Louisa Community Bank	                            LCNB
#    The Enloe State Bank	                            ESBK
#    Washington Federal Bank for Savings	            WFB
#    The Farmers and Merchants State Bank of Argonia	FMS
#    Fayette County Bank	                            FABK
#    Guaranty Bank	                                    GTBK (delisted)
#    First NBC Bank	                                    FNB
#    Proficio Bank	                                    PFBC (delisted)
#    Seaway Bank and Trust Company	                    SEBC
#    Harvest Community Bank	                            HCBN
#    Allied Bank	                                    ALBK (delisted)
#    The Woodbury Banking Company	                    WBCO
#    First CornerStone Bank	                            FCNK
#    Trust Company Bank	                                TCB
#    North Milwaukee State Bank	                        NMSB
#    Hometown National Bank	                            HTNB
#    The Bank of Georgia	                            TBOG
#    Premier Bank	                                    PBNK
#    Edgebrook Bank	                                    EBDK
#    Doral Bank	                                        DBNK
#    Capitol City Bank & Trust Company	                CCBT
#    Highland Community Bank	                        HCBK

#%% END

