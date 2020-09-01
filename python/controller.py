from atm import Atm
from session import Session
from csvReader import CsvReader
from transaction import Transaction
import os
import utilities
import logging

class Controller:
	def __init__(self,startingCash=10000):
		self.__atm = Atm(startingCash=startingCash)

		dir_path = os.path.dirname(os.path.realpath(__file__))
		relativePath = "../csv/"
		path = os.path.abspath(os.path.join(dir_path, relativePath))
		csvReader = CsvReader(filename="/bankingInfo.csv",path=path)
		df = csvReader.readCsvIntoDf()
		self.__accounts = csvReader.createAccountsUsingDf(df)
		self.__currentSession = Session()

		# initializing the log
		# a sample log is enclosed in this repo
		logging.basicConfig(filename="controller.log", 
							level=logging.DEBUG,
							format="%(asctime)s | %(name)s | %(levelname)s | %(message)s")
		logging.info(f"The following new controller object was initialized:{self}")

	def __str__(self):
		return f"Controller:{{{self.getAtm()},accounts:{self.getLatestAccountInfo()},{self.getCurrentSession()}}}"

	def __repr__(self):
		return self.__str__()

	def getAtm(self):
		return self.__atm

	# retreiving latest account info whenever needed
	def getLatestAccountInfo(self):
		return self.__accounts

	def getCurrentSession(self):
		return self.__currentSession

	def setCurrentSession(self,currentSession):
		self.__currentSession = currentSession

	# input: authorize <account_id> <pin>
	def authorize(self,accountId,pin):
		logging.debug(f"Controller at the start of login:{self}")
		string = ""

		if accountId not in self.getLatestAccountInfo().keys() :
			string = "Authorization failed due to invalid accountId"
			return string 

		# if there is already a session with another user, I won't allow a fresh login 
		if self.getCurrentSession().getCurrentAccountId() is not None and self.getCurrentSession().getCurrentAccountId() != accountId:
			string = "Another user is already authorized. Please try again later"
			logging.warning(f"AccountId {accountId} failed to log in since another user is already logged in")
			return string

		# fresh session and authorize the user
		authorized = self.getCurrentSession().authorize(accounts=self.getLatestAccountInfo(),accountId=accountId,pin=pin)
		if authorized:
			string = f"{accountId} successfully authorized"
		else:
			string = "Authorization failed."

		logging.debug(f"Controller at the end of login:{self}")
		return string

	# input: balance
	def balance(self):
		logging.debug(f"Controller at the start of balance:{self}")
		string = ""
		authorized = self.getCurrentSession().checkAuthorizationStatus()

		if authorized: 
			logging.info(f"AccountId {self.getCurrentSession().getCurrentAccountId()} successfully authorized to access their account balance")
			balance = self.getCurrentSession().getBalance(accounts=self.getLatestAccountInfo())
			string = f"Current balance: {utilities.displayCash(balance)}"
			logging.debug(f"Controller at the end of successful balance check:{self}")
		else: 
			string = "Authorization required."
			logging.warning("Get balance failed because the current user is not authorized")

		return string

	# input: deposit <value>
	def deposit(self,value):
		logging.debug(f"Value:{value}, controller at the start of deposit:{self}")
		string = ""
		authorized = self.getCurrentSession().checkAuthorizationStatus()

		if authorized: 
			self.getCurrentSession().deposit(self.getLatestAccountInfo(),self.getAtm(),value)

			# check and return new balance after deposit
			string = self.balance()
			logging.debug(f"Controller at the end of deposit:{self}")
		else:
			string = "Authorization required."
			logging.warning(f"Deposit failed because the current user is not authorized")

		return string

	# input: withdraw <value>
	def withdraw(self,value):
		logging.debug(f"Value:{value}, controller at the start of deposit:{self}")
		string = ""
		authorized = self.getCurrentSession().checkAuthorizationStatus()

		if authorized: 

			# if the user is overdrawn, stop the user from making the withdrawal immediately
			if self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].getOverdrawnStatus(): 
				logging.warning(f"AccountId {self.getCurrentSession().getCurrentAccountId()} attempted withdrawal with overdrawn accouunt. Balance={self.getCurrentSession().getBalance(accounts=self.getLatestAccountInfo())}")
				string = "Your account is overdrawn! You may not make withdrawals at this time."
				return string

			# if the ATM has no money, inform the user and end the transaction
			# i won't be adding a transaction to transaction history for this
			if self.getAtm().getCurrentCash() == 0: 
				logging.warning("Withdrawal was cancelled because the ATM is out of money")
				string = "Unable to process your withdrawal at this time."
				return string
			if value < 0:
				logging.warning(f"Withdrawal value less than 0 was passed into withdrawal function: value={value}")
				string = "You must request a withdrawal a value greater than 0"
				return string
			if value == 0:
				logging.warning("Withdrawal value of 0 was passed into withdrawal function. Withdrawals must be greater than 0")
				string = "Please request a withdrawal of a non-zero amount of money"
				return string
			if value%20 != 0:
				logging.warning(f"A withdrawal value that is not a multiple of $20 was passed into withdrawal function: value={value}")
				string = f"Withdrawal amount must be a multiple of $20"
				return string

			# running the withdrawal and storing if the ATM had the required cash for the transaction
			withdrawnValue = self.getCurrentSession().withdraw(accounts=self.getLatestAccountInfo(),atm=self.getAtm(),value=value)
			overdrafting = self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].getOverdrawnStatus()

			newBalance = self.getCurrentSession().getBalance(accounts=self.getLatestAccountInfo())

			# if the ATM didn't have enough money
			if withdrawnValue != value :
				string = "Unable to dispense full amount requested at this time.\n"

			if overdrafting:
				string += f"Amount dispensed: ${utilities.displayCash(withdrawnValue)}\n"
				string += f"You have been charged an overdraft fee of $5. Current balance: {utilities.displayCash(newBalance)}"
			else: 
				string += f"Amount dispensed: ${utilities.displayCash(withdrawnValue)}\n"
				string += self.balance()

			logging.debug(f"Controller at the end of withdrawal:{self}")
		else:
			string = "Authorization required."
			logging.warning(f"Withdrawal failed because the current user is not authorized")
		
		return string

	# input: history
	def history(self):
		logging.debug(f"Controller at the start of deposit:{self}")
		string = ""
		authorized = self.getCurrentSession().checkAuthorizationStatus() 

		if authorized:
			transactionHistory = self.getCurrentSession().history(accounts=self.getLatestAccountInfo())
			if len(transactionHistory) is None:
				string = "No history found"
			else: 
				for transaction in transactionHistory: 
					string += str(transaction)+"\n"
		else:
			string = "Authorization required."

		return string


	# input: logout
	def logout(self):
		logging.debug(f"Controller at the start of logout:{self}")
		string=""
		wasAuthorized = self.getCurrentSession().checkAuthorizationStatus()

		# user was authorized
		if wasAuthorized: 
			accountId = self.getCurrentSession().getCurrentAccountId()
			self.setCurrentSession(currentSession=Session())
			string = f"Account {accountId} logged out."
			logging.debug(f"Controller at the end of logout:{self}")
		# if the user was not authorized
		else:
			string = f"No Account is currently authorized"
			logging.warning(f"Logout was terminated because no user is currently logged in")

		return string

# helper function to send help text back to the user
def help(keyword=None):
	startText = "Please enter the following format for "

	helpText = {}
	helpText["authorize"] = "authorize <account_id> <pin>"
	helpText["logout"] = "logout"
	helpText["balance"] = "balance"
	helpText["history"] = "history"
	helpText["deposit"] = "deposit <value>"
	helpText["withdraw"] = "withdraw <value>"
	if keyword is not None:
		# all strings for a given keyword look the same
		helpString = startString + keyword + ": " + helpText[keyword]
		helpString += "\nFor additional syntax help, please type in the following command: help"

	else:
		helpString = "The following are the supported commands for this banking system:\n"
		for key in helpText.keys():
			helpString += helpText[key] + "\n"

	return helpString




# main handles all the text input
if __name__ == "__main__":
	controller = Controller()
	text = ""
	while text != "end":
		print("Please enter a command: ")
		text = input().strip()

		wordList = text.split(" ")

		if len(wordList)==0:
			print("Please enter some text") 
			continue

		# handling different input
		if wordList[0] == "authorize":
			if len(wordList) != 3:
				print(help(keyword=wordList[0]))
				continue
			if not utilities.isInt(wordList[2]):
				print("Pin needs to be an integer")
				continue
			accountId = wordList[1]
			pin = int(wordList[2])
			controller.authorize(accountId=accountId,pin=pin)
		elif wordList[0] == "logout":
			if len(wordList) != 1:
				print(help(keyword=wordList[0]))
				continue
			print(controller.logout())
		elif wordList[0] == "balance":
			if len(wordList) != 1:
				print(help(keyword=wordList[0]))
				continue
			controller.balance()
		elif wordList[0] == "history":
			if len(wordList) != 1:
				print(help(keyword=wordList[0]))
				continue
			print(controller.history())
		elif wordList[0] == "deposit":
			if len(wordList) != 2:
				print(help(keyword=wordList[0]))
				continue
			value = int(wordList[1])
			controller.deposit(value=value)
		elif wordList[0] == "withdraw":
			if len(wordList) != 2:
				print(help(keyword=wordList[0]))
				continue
			value = int(wordList[1])
			print(controller.withdraw(value=value))
		elif wordList[0] == "help":
			print(help())
		elif wordList[0] == "end" :
			break
		else:
			# help helper function
			# use help to store individual errors as well typed out above
			print("Please enter a proper command")
			continue





