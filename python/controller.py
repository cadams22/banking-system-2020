from atm import Atm
from session import Session
from readCsvIntoAccounts import ReadCsvIntoAccounts
from transaction import Transaction
import os

class Controller:
	def __init__(self):
		self.atm = Atm(startingCash=10000)

		dir_path = os.path.dirname(os.path.realpath(__file__))
		relativePath = "../csv/"
		path = os.path.abspath(os.path.join(dir_path, relativePath))
		csvReader = ReadCsvIntoAccounts(filename='/bankingInfo.csv',path=path)
		df = csvReader.readCsvIntoDf()
		self.__accounts = csvReader.createAccountsUsingDf(df)
		self.__currentSession = None

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
		if self.getCurrentSession() is not None and self.currentSession.getCurrentAccountId() != accountId:
			print("Another user is already authorized. Please try again later")
			return 

		# fresh session and authorize the user
		self.setCurrentSession(Session(currentAccountId=accountId))
		self.getCurrentSession().authorize(accounts=self.getLatestAccountInfo(),accountId=accountId,pin=pin)

	# input: balance
	def balance(self):
		# we check if the user is authorized in currentSession.getBalance
		# i did this so because i wanted to make sure there was no way to access balance without being authorized
		balance = self.getCurrentSession().getBalance(accounts=self.getLatestAccountInfo())
		print(f"Current balance: {balance}")
		return balance

	# input: deposit <value>
	def deposit(self,value):
		if value < 0:
			print("You must deposit a value greater than 0")
			return
		if value == 0:
			print("Please deposit a non-zero amount of money")
			return 

		balance = self.balance()
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

		print(f"Current balance: {newBalance}")

	# input: withdraw <value>
	def withdraw(self,value):
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
			print("You must request a withdrawl a value greater than 0")
			return
		if value == 0:
			print("Please request a withdrawl of a non-zero amount of money")
			return 
		if value%20 != 0:
			print(f"Withdrawal amount must be a multiple of $20")
			return

		balance = self.balance()
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
				value -= 5

			print("Unable to dispense full amount requested at this time.")

		newBalance = balance - value

		self.atm.setCurrentCash(cash=self.atm.getCurrentCash()-value)
		self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].setBalance(balance=newBalance)

		if overdrafting:
			self.accounts[self.getCurrentSession().getCurrentAccountId()].setOverDrawnStatus(overdrawn=True)
			print(f"Amount dispensed: ${value}")
			print(f"You have been charged an overdraft fee of $5. Current balance: {newBalance}")
		else: 
			print(f"Amount dispensed: ${value}")
			print(f"Current balance: {newBalance}")

		# creating a new transaction for this withdrawl and adding it to the account's txn history
		transaction = Transaction(transactionAmount=-value,remainingBalance=newBalance)
		self.getLatestAccountInfo()[self.getCurrentSession().getCurrentAccountId()].addTransactionToHistory(transaction)

	# input: history
	def history(self):
		transactionHistory = self.accounts[self.getCurrentSession().getCurrentAccountId()].getTransactionHistory()
		if len(transactionHistory) == 0:
			print("No history found")
		else: 
			for transaction in transactionHistory: 
				print(transaction)

	# input: logout
	def logout(self):
		wasAuthorized = self.getCurrentSession().checkAuthorizationStatus()

		# user was authorized
		if wasAuthorized: 
			accountId = self.getCurrentSession().getCurrentAccountId()
			self.setCurrentSession(currentSession=None)
			print(f"Account {accountId} logged out.")
		# if the user was not authorized
		else:
			print(f"No Account is currently authorized")

# make sure to write code to end the program on input end
# most likely, i will implement this inside of main, when i implement main