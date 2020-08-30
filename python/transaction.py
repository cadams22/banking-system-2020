from datetime import datetime

class Transaction: 
	def __init__(self,transactionAmount=None,remainingBalance=None):
		now = datetime.now()
		self.__date = now.strftime("%Y-%m-%d")
		self.__time = now.strftime("%H:%M:%S")
		self.__transactionAmount = transactionAmount
		self.__remainingBalance = remainingBalance

	def __str__(self):
		return f"{self.getTransactionDate()} {self.getTransactionTime()} {self.getTransactionAmount()} {self.getRemainingBalance()}"

	def getTransactionDate():
		return self.__date

	def getTransactionTime():
		return self.__time

	def getTransactionAmount():
		return self.__transactionAmount

	def getRemainingBalance():
		return self.__remainingBalance