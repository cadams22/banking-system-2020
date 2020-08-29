import utilities
import pandas as pd
from account import Account

class ReadCsvIntoAccounts:
	def __init__(self,filename,relativePath='../csv/'):

		# i keep the csv in path ../csv/ relative to the location of this script
		# but i allow this to be configurable by the caller of this class
		self.relativePath = relativePath
		# this is the name of the csv I am 
		self.filename = filename

	# purposefully keeping the names and concepts of these functions very loose
	# to encourage reuse
	# reading a csv into a dataframe is something i do all of the time in my day-to-day
	# and then i may decide to move these to utilities.py
	def readCsvIntoDf(self):

		# dataframe of banking info
		# specifying that the first line of this file is a header
		# todo: how do we want to handle duplicate account ids? override?
		try: 
			df = utilities.readCsv(relativePath=self.relativePath,filename=self.filename)
		except pd.errors.EmptyDataError as e:
			print('Empty CSV file passed in. Please pass in a file that has, at a minimum, headers')
			raise e
		return df

	def createAccountsUsingDf(self,df):
		# todo: handle empty dataframe
		accounts = {}

		# iterating through the dataframe and keeping track of info for each account
		for index, row in df.iterrows(): 
			accountId = int(row["ACCOUNT_ID"])
			pin = int(row["PIN"])
			balance = float(row["BALANCE"])

			# read Account.py to understand Account class
			# accounts have an ID, PIN and balance 
			accounts[accountId] = Account(accountId=accountId,pin=pin,balance=balance)

		return accounts