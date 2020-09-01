from datetime import datetime, timedelta
from transaction import Transaction

# this class contains helpers related to a Session
# i define the scope of a Session to be when a user logs in until they log on
# when the user logs out, a new empty Session is created
class Session:
	def __init__(self,currentAccountId=None):
		self.__currentAccountId = currentAccountId
		self.__authorizationTime = None

	def __str__(self):
		return f"Session:{{currentAccountId:{self.getCurrentAccountId()}, authorizationTime:{self.getAuthorizationTime()}}}"

	def __repr__(self):
		return self.__str__()

	def getCurrentAccountId(self):
		return self.__currentAccountId

	def setCurrentAccountId(self,currentAccountId):
		self.__currentAccountId = currentAccountId

	def getAuthorizationTime(self):
		return self.__authorizationTime

	def setAuthorizationTime(self):
		# i am not letting authorization time get set to anything but right now
		self.__authorizationTime = datetime.now()

	def clearAuthorizationTime(self):
		# i am not letting authorization time get set to anything but right now
		self.__authorizationTime = None

	# if the user is still authorized, return True. otherwise, return False
	# the user is still authorized if there has been account activity in the last 120 seconds 
	def checkAuthorizationStatus(self):
		# if the current time is less than previous authorization time + 120 seconds return True
		if self.getAuthorizationTime() is not None and datetime.now() <= self.getAuthorizationTime() + timedelta(seconds=119):
			# good news. this user is still authorized
			# we reset the authorization time
			self.setAuthorizationTime()
			return True
		else: 
			return False

	# if the user is successfully authorized, return True. If authorization failed, return False
	def authorize(self,accounts,accountId,pin):
		if pin == accounts[accountId].getPin():
			self.setCurrentAccountId(accountId)
			self.setAuthorizationTime()
			return True
		else:
			return False
		
	# the controller will call this after fetching the latest activity on the classes
	def getBalance(self,accounts):
		# i get the latest account info, search for the current authorized account
		# and return the balance using the getter from the Account class
		return accounts[self.getCurrentAccountId()].getBalance()

	def deposit(self,accounts,atm,value):
		if value < 0:
			print("You must deposit a value greater than 0")
			return
		if value == 0:
			print("Please deposit a non-zero amount of money")
			return 

		balance = self.getBalance(accounts=accounts)
		# new account balance = existing balance plus freshly-deposited cash
		newBalance = balance + value
		# the atm now has more money available
		atm.setCurrentCash(cash=atm.getCurrentCash()+value)

		# setting the account balance to the new balance
		accounts[self.getCurrentAccountId()].setBalance(balance=newBalance)

		# if account is overdrawn and the newBalance is greater than or equal to zero
		# then the account is no longer overdrawn
		if accounts[self.getCurrentAccountId()].getOverdrawnStatus():
			accounts[self.getCurrentAccountId()].setOverdrawnStatus(False)
			
		# creating a new transaction for this deposit and adding it to the account's txn history
		transaction = Transaction(transactionAmount=value,remainingBalance=newBalance)
		accounts[self.getCurrentAccountId()].addTransactionToHistory(transaction)

		return value

	def withdraw(self,accounts,atm,value):
		atmCurrentCash = atm.getCurrentCash()
		overdrafting = False

		balance = self.getBalance(accounts=accounts)
		newBalance = balance

		# if the account is overdrafting, we remove an additional $5 from the account 
		if balance - value < 0: 
			overdrafting = True

		# the new currentCash balance of the ATM is the old value minus the value withdrawn
		atmNewCurrentCash = atmCurrentCash - value

		# ...but what if this value is less than zero?
		if atmNewCurrentCash < 0: 
			# the ATM does not have enough cash for the transaction
			# the value withdrawn equals to all the money left in the ATM
			value = atmCurrentCash
			atmNewCurrentCash = 0

			# maybe i'm a nice banker
			# but if the ATM cannot afford to let the user overdraft,
			# i'm going to remove the $5 charge for them :)
			if overdrafting and balance - value >= 0:
				overdrafting = False

		newBalance -= value
		if overdrafting:
			newBalance -= 5

		atm.setCurrentCash(cash=atmNewCurrentCash)
		accounts[self.getCurrentAccountId()].setBalance(balance=newBalance)

		if overdrafting:
			accounts[self.getCurrentAccountId()].setOverdrawnStatus(overdrawn=True)

		# creating a new transaction for this withdrawal and adding it to the account's txn history
		transaction = Transaction(transactionAmount=-value,remainingBalance=newBalance)
		accounts[self.getCurrentAccountId()].addTransactionToHistory(transaction)

		return value

	def history(self,accounts):
		return accounts[self.getCurrentAccountId()].getTransactionHistory()

