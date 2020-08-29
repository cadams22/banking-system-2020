# i am only first starting this class
# i may remove this class or expand it

class Atm:
	# i decided to leave this flexible, in case ATMs may start their life with
	# more or less than $10,000
	def __init__(self,currentCash=10000):
		self.__currentCash=currentCash

	def getCurrentCash(self):
		return self.__currentCash