from readCsvIntoAccounts import ReadCsvIntoAccounts
from datetime import datetime, timedelta

class Session:
	def __init__(self,currentAccountId=None):
		self.__transactions = {}
		self.__currentAccountId = currentAccountId
		self.__authorizationTime = None

	def appendTransaction(self,transaction):
		# keeping track of each individual transaction for a given session
		self.__transactions.append(transaction)

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
		print(datetime.now())
		if self.getAuthorizationTime() is not None:
			print(self.getAuthorizationTime() + timedelta(seconds=120))
		else:
			print("authorizationTime is null")
		# if the current time is less than previous authorization time + 120 seconds return True
		if self.getAuthorizationTime() is not None and datetime.now() < self.getAuthorizationTime() + timedelta(seconds=120):
			# good news. this user is still authorized
			# we reset the authorization time
			self.setAuthorizationTime()
			return True
		else: 
			return False

	def authorize(self,accounts,accountId,pin):
		if accountId not in accounts.keys():
			print('Authorization failed due to invalid accountId')
			return

		if pin == accounts[accountId].getPin():
			print(f'{accountId} successfully authorized')
			self.setCurrentAccountId(accountId)
			self.setAuthorizationTime()
		else:
			print(f'Authorization failed.')
		
	# the controller will call this after fetching the latest activity on the classes
	def getBalance(self,accounts):
			# i get the latest account info, search for the current authorized account
			# and return the balance using the getter from the Account class
			return accounts[self.getCurrentAccountId()].getBalance()