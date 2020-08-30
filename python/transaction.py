from datetime import datetime
import utilities

class Transaction: 
	def __init__(self,transactionAmount=None,remainingBalance=None):
		now = datetime.now()
		self.__date = now.strftime("%Y-%m-%d")
		self.__time = now.strftime("%H:%M:%S")
		self.__transactionAmount = transactionAmount
		self.__remainingBalance = remainingBalance

	def __str__(self):
		return f"{self.getTransactionDate()} {self.getTransactionTime()} {utilities.displayCash(self.getTransactionAmount())} {utilities.displayCash(self.getRemainingBalance())}"

	def getTransactionDate(self):
		return self.__date

	def getTransactionTime(self):
		return self.__time

	def getTransactionAmount(self):
		return self.__transactionAmount

	def getRemainingBalance(self):
		return self.__remainingBalance