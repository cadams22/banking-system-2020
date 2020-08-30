from atm import Atm
from session import Session
from readCsvIntoAccounts import ReadCsvIntoAccounts
from transaction import Transaction
import os
import utilities

class Controller:
	def __init__(self):
		self.atm = Atm(startingCash=10000)

		dir_path = os.path.dirname(os.path.realpath(__file__))
		relativePath = "../csv/"
		path = os.path.abspath(os.path.join(dir_path, relativePath))
		csvReader = ReadCsvIntoAccounts(filename="/bankingInfo.csv",path=path)
		df = csvReader.readCsvIntoDf()
		self.__accounts = csvReader.createAccountsUsingDf(df)
		self.__currentSession = Session()

	# retreiving latest account info whenever needed
	def getLatestAccountInfo(self):
		return self.__accounts

	def getCurrentSession(self):
		return self.__currentSession

	def setCurrentSession(self,currentSession):
		self.__currentSession = currentSession

	# input: authorize <account_id> <pin>
	def login(self,accountId,pin):
		# if there is already a session with another user, I won't allow a fresh login 
		if self.getCurrentSession().getCurrentAccountId() is not None and self.getCurrentSession().getCurrentAccountId() != accountId:
			print("Another user is already authorized. Please try again later")
			return 

		# fresh session and authorize the user
		self.getCurrentSession().authorize(accounts=self.getLatestAccountInfo(),accountId=accountId,pin=pin)

	# input: balance
	def balance(self):
		authorized = self.getCurrentSession().checkAuthorizationStatus()

		if authorized: 
			balance = self.getCurrentSession().getBalance(accounts=self.getLatestAccountInfo())
			print(f"Current balance: {utilities.displayCash(balance)}")
			return balance
		else: 
			print("Authorization required.")

	# input: deposit <value>
	def deposit(self,value):
		authorized = self.getCurrentSession().checkAuthorizationStatus()

		if authorized: 
			if value < 0:
				print("You must deposit a value greater than 0")
				return
			if value == 0:
				print("Please deposit a non-zero amount of money")
				return 

			balance = self.getCurrentSession().getBalance(accounts=self.getLatestAccountInfo())
			# new account balance = existing balance plus freshly-deposited cash
			newBalance = balance + value
			# the atm now has more money available
			self.atm.setCurrentCash(cash=self.atm.getCurrentCash()+value)

			# setting the account balance to the new balance
			self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].setBalance(balance=newBalance)

			# if account is overdrawn and the newBalance is greater than or equal to zero
			# then the account is no longer overdrawn
			if self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].getOverdrawnStatus():
				self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].setOverdrawnStatus(False)
			
			# creating a new transaction for this deposit and adding it to the account's txn history
			transaction = Transaction(transactionAmount=value,remainingBalance=newBalance)
			self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].addTransactionToHistory(transaction)

			print(f"Current balance: {utilities.displayCash(newBalance)}")
			return True
		else:
			print("Authorization required.")
			return False

	# input: withdraw <value>
	def withdraw(self,value):
		authorized = self.getCurrentSession().checkAuthorizationStatus()

		if authorized: 
			atmCurrentCash = self.atm.getCurrentCash()

			# if the user is overdrawn, stop the user from making the withdrawal immediately
			if self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].getOverdrawnStatus(): 
				print(f"Your account is overdrawn! You may not make withdrawals at this time.")
				return

			# if the ATM has no money, inform the user and end the transaction
			# i won't be adding a transaction to transaction history for this
			if atmCurrentCash == 0: 
				print(f"Unable to process your withdrawal at this time.")
				return

			if value < 0:
				print("You must request a withdrawal a value greater than 0")
				return
			if value == 0:
				print("Please request a withdrawal of a non-zero amount of money")
				return 
			if value%20 != 0:
				print(f"Withdrawal amount must be a multiple of $20")
				return

			balance = self.getCurrentSession().getBalance(accounts=self.getLatestAccountInfo())
			# by default, i am assuming the user is not overdrafting
			overdrafting = False

			# if the account is overdrafting, we remove an additional $5 from the account 
			if balance - value < 0: 
				value += 5
				overdrafting = True

			# the new currentCash balance of the ATM is the old value minus the value withdrawn
			atmNewCurrentCash = atmCurrentCash - value

			# ...but what if this value is less than zero?
			if atmNewCurrentCash < 0: 
				# the value withdrawn equals to all the money left in the ATM
				value = atmCurrentCash

				# maybe i'm a nice banker
				# but if the ATM cannot afford to let the user overdraft,
				# i'm going to remove the $5 charge for them :)
				if overdrafting and balance - value >= 0:
					overdrafting = False

				print("Unable to dispense full amount requested at this time.")

			newBalance = balance - value

			self.atm.setCurrentCash(cash=self.atm.getCurrentCash()-value)
			self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].setBalance(balance=newBalance)

			if overdrafting:
				self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].setOverdrawnStatus(overdrawn=True)
				print(f"Amount dispensed: ${utilities.displayCash(value)}")
				print(f"You have been charged an overdraft fee of $5. Current balance: {utilities.displayCash(newBalance)}")
			else: 
				print(f"Amount dispensed: ${utilities.displayCash(value)}")
				print(f"Current balance: {utilities.displayCash(newBalance)}")

			# creating a new transaction for this withdrawal and adding it to the account's txn history
			transaction = Transaction(transactionAmount=-value,remainingBalance=newBalance)
			self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].addTransactionToHistory(transaction)
			return True
		else:
			print("Authorization required.")
			return False

	# input: history
	def history(self):
		transactionHistory = []
		authorized = self.getCurrentSession().checkAuthorizationStatus() 
		if authorized:
			transactionHistory = self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].getTransactionHistory()
			if len(transactionHistory) == 0:
				print("No history found")
			else: 
				for transaction in transactionHistory: 
					print(transaction)
			return transactionHistory
		else:
			print("Authorization required.")


	# input: logout
	def logout(self):
		wasAuthorized = self.getCurrentSession().checkAuthorizationStatus()

		# user was authorized
		if wasAuthorized: 
			accountId = self.getCurrentSession().getCurrentAccountId()
			self.setCurrentSession(currentSession=Session())
			print(f"Account {accountId} logged out.")
		# if the user was not authorized
		else:
			print(f"No Account is currently authorized")

# make sure to write code to end the program on input end
# most likely, i will implement this inside of main, when i implement main
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
				print("Please enter the following format for authorize: authorize <account_id> <pin>")
				continue
			if not utilities.isInt(wordList[2]):
				print("Pin needs to be an integer")
				continue
			accountId = wordList[1]
			pin = int(wordList[2])
			controller.login(accountId=accountId,pin=pin)
		elif wordList[0] == "logout":
			if len(wordList) != 1:
				print("Please enter the following format for logout: logout")
				continue
			controller.logout()
		elif wordList[0] == "balance":
			if len(wordList) != 1:
				print("Please enter the following format for balance: balance")
				continue
			controller.balance()
		elif wordList[0] == "history":
			if len(wordList) != 1:
				print("Please enter the following format for history: history")
				continue
			controller.history()
		elif wordList[0] == "deposit":
			if len(wordList) != 2:
				print("Please enter the following format for deposit: deposit <value>")
				continue
			value = int(wordList[1])
			controller.deposit(value=value)
		elif wordList[0] == "withdraw":
			if len(wordList) != 2:
				print("Please enter the following format for withdraw: withdraw <value>")
				continue
			value = int(wordList[1])
			controller.withdraw(value=value)
		elif wordList[0] == "end" :
			break
		else:
			# help helper function
			# use help to store individual errors as well typed out above
			print("Please enter a proper command")
			continue





