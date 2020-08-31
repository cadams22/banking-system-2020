class Account:
	# accountId needs to be passed in
	# assuming that accounts can be created with no PIN
	# if no balance is provided, assume the account has no balance
	def __init__(self,accountId,pin=None,balance=0.00):
		# making all attributes private using __ prefix
		# typically i would make these public in alignment with UAP https://en.wikipedia.org/wiki/Uniform_access_principle
		# but i want to restrict access to setting and getting accountId. therefore, i kept it consistent
		# everything is private 
		self.__accountId = accountId
		self.__pin = pin
		self.__balance = balance 
		self.__overdrawn = False
		# keep track of transaction history
		self.__transactionHistory = []

	# unless there is another requirement, i like to make the strings JSON format
	def __str__(self):
		return f"Account:{{accountId:{self.getAccountId()},pin:****,balance:{self.getBalance()},overdrawn:{self.getOverdrawnStatus()},getTransactionHistory:{self.getTransactionHistory()}}}"

	def __repr__(self):
		return self.__str__()

	# public functions for getters and setters
	# we do not allow a user to modify their account ID (getter no setter)
	def getAccountId(self):
		return self.__accountId

	def getPin(self):
		return self.__pin

	def setPin(self,pin): 
		self.__pin = pin

	def getBalance(self):
		return self.__balance

	def setBalance(self,balance):
		self.__balance = balance

	def getOverdrawnStatus(self):
		return self.__overdrawn

	def setOverdrawnStatus(self,overdrawn):
		self.__overdrawn = overdrawn

	def getTransactionHistory(self):
		return self.__transactionHistory

	def addTransactionToHistory(self,transaction):
		# adding the most recent transaction to the start of the list (index 0)
		self.__transactionHistory.insert(0, transaction)