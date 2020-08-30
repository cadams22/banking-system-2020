# i am only first starting this class
# i may remove this class or expand it

class Atm:
	# i decided to leave this flexible, in case ATMs may start their life with
	# more or less than $10,000
	def __init__(self,startingCash=10000):
		self.__availableCash=startingCash
		# not required but i will store all transactions run on a given ATM
		# i think this could be useful 
		self.__transactionHistory = []
		self.__currentSession = None

	def getCurrentCash(self):
		return self.__availableCash

	def setCurrentCash(self,cash) :
		#if currentCash <0 : raise exception
		self.__availableCash = cash 

	def getTransactionHistory(self):
		return self.__transactionHistory

	def appendToTransactionHistory(self,transaction):
		self.__transactionHistory.append(transaction)

	def getCurrentSessions(self):
		return self.__currentSession

	def setCurrentSession(self,session):
		self.__currentSession = session