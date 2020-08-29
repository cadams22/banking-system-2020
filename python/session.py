from readCsvIntoAccounts import ReadCsvIntoAccounts
from datetime import datetime, timedelta


class Session:
	def __init__(self):
		self.__transactions = {}
		self.__currentAccountId = None
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

	# i decided not to return boolean because I want to provide three outputs
	# 0: no user has an active session
	# 1: current user is authorized (traditional True output)
	# 2: current user is not authorized but another user has an active session 
	# for output == 2: we want to prevent the new user from authorizing 
	def checkAuthorizationStatus(self,accountId=None):
		# if no ID is passed in, i'm assuming we're discussing current user
		if accountId is None:
			accountId = self.getCurrentAccountId()

		# keeping "now" consistent for all checks
		now = datetime.now()
		# if the current time is greater than previous authorization time + 120 seconds
		# return 0 - no user (including current) has an active session
		if self.getAuthorizationTime() is None or now > self.getAuthorizationTime() + timedelta(seconds=120): 
			self.setCurrentAccountId(currentAccountId=None)
			self.clearAuthorizationTime()
			return 0

		# if we got here, a user is authorized
		if self.getCurrentAccountId() == accountId:
			# good news. this user is still authorized
			# we reset the authorization time
			self.setAuthorizationTime()
			return 1
		else: 
			# another user has a session. this new user will have to wait
			return 2

	def authorize(self,accounts,accountId,pin):
		if accountId not in accounts.keys():
			print('Authorization failed due to invalid accountId')
			return

		# 0 means no one is authorized
		# 1 means the user is already authorized. i am ok with the user reauthorizing 
		if self.checkAuthorizationStatus(accountId=accountId) in [0,1]:
			if pin == accounts[accountId].getPin():
				print(f'{accountId} successfully authorized')
				self.setCurrentAccountId(accountId)
				self.setAuthorizationTime()
			else:
				print(f'Authorization failed.')
		# check authorization status returns 2 when another user is logged in
		else:
			print(f'Authorization failed because another user is logged in. Please wait until they are done')

	# the controller will call this after fetching the latest activity on the classes
	def getBalance(self,accounts):
		if self.checkAuthorizationStatus() == 1:
			# i get the latest account info, search for the current authorized account
			# and return the balance using the getter from the Account class
			return accounts[self.getCurrentAccountId()].getBalance()