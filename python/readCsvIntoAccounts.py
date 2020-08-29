from account import Account
import utilities

# i keep the csv in path ../csv/ relative to the location of this script
csvRelativePath = '../csv/'
# this is the name of the csv I am 
csvFilename = 'bankingInfo.csv'

# dataframe of banking info
# specifying that the first line of this file is a header
bankingDf = utilities.readCsv(relativePath=csvRelativePath,filename=csvFilename)

# iterating through the dataframe and keeping track of info for each account
for index, row in bankingDf.iterrows(): 
	accountId = int(row["ACCOUNT_ID"])
	pin = int(row["PIN"])
	balance = row["BALANCE"]

	# read Account.py to understand Account class
	# accounts have an ID, PIN and balance 
	account = Account(accountId=accountId,pin=pin,balance=balance)

	print(account.getAccountId())