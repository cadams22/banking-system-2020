# i am only first starting this class
# i may remove this class or expand it

class Atm:
	# i decided to leave this flexible, in case ATMs may start their life with
	# more or less than $10,000
	def __init__(self,startingCash=10000):
		self.__availableCash=startingCash

	def __str__(self):
		return f"Atm:{{availableCash:{self.getCurrentCash()}}}"

	def __repr__(self):
		return self.__str__()
	
	def getCurrentCash(self):
		return self.__availableCash

	def setCurrentCash(self,cash) :
		#if currentCash <0 : raise exception
		self.__availableCash = cash 