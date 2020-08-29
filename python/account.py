class Account:
	# accountId needs to be passed in
	# assuming that accounts can be created with no PIN
	# if no balance is provided, assume the account has no balance
	def __init__(self,accountId,pin=None,balance=0.00):
		# making all attributes private using __ prefix
		self.__accountId = accountId
		self.__pin = pin
		self.__balance = balance 

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