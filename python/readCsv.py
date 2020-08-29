# using the pandas library to read the csv file into a dataframe
# may move this to a utilities.py file since csv reading is useful for many purposes
import pandas as pd
from account import Account

# i keep the csv here
csvPath = '../csv/'
# this is the name of the csv I am 
csvFilename = 'bankingInfo.csv'
# full path for the csv
csvPathFile = csvPath + csvFilename

# dataframe of banking info
# specifying that the first line of this file is a header
bankingDf = pd.read_csv(csvPathFile)

# iterating through the dataframe and keeping track of info for each account
for index, row in bankingDf.iterrows(): 
	accountId = int(row["ACCOUNT_ID"])
	pin = int(row["PIN"])
	balance = row["BALANCE"]

	# read Account.py to understand Account class
	# accounts have an ID, PIN and balance 
	account = Account(accountId=accountId,pin=pin,balance=balance)

	print(account.getAccountId())