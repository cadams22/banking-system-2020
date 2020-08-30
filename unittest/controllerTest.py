import unittest
import os
import sys

currentDirectory = os.path.dirname(__file__)
relativePath = '../python/'
path = os.path.join(currentDirectory, relativePath)

sys.path.insert(1, path)

from controller import Controller
from readCsvIntoAccounts import ReadCsvIntoAccounts

class TestController(unittest.TestCase):
	def setUp(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		relativePath = "../csv/"
		self.path = os.path.abspath(os.path.join(dir_path, relativePath))

		csvReader = ReadCsvIntoAccounts(filename='/bankingInfo.csv',path=self.path)
		df = csvReader.readCsvIntoDf()
		self.accounts = csvReader.createAccountsUsingDf(df)

	def testInit(self):
		controller = Controller()

		self.assertEquals(len(controller.getLatestAccountInfo()),4)

	def testLogin(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())

		# check that after login, the user is currently authorized
		self.assertEquals(controller.getCurrentSession().checkAuthorizationStatus(),True)

	def testBalance(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())
		balance = controller.balance()

		# check that the controller is getting the right balance
		self.assertEquals(balance,self.accounts[accountId].getBalance())

	def testDeposit(self):
		value = 1

		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())
		oldBalance = controller.balance()
		controller.deposit(value=value)
		balance = controller.balance()

		# check that after deposit, the balance equals old balance minus one
		self.assertEquals(balance,oldBalance+1)

	def testWithdrawl(self):
		value = 20

		controller = Controller()
		accountId = list(self.accounts.keys())[1]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())
		oldBalance = controller.balance()
		controller.withdraw(value=value)
		balance = controller.balance()

		# check that after deposit, the balance equals old balance minus one
		self.assertEquals(balance,oldBalance-value)

	def testLogout(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())

		controller.logout()

		# check that after logout, the user is no longer authorized
		self.assertIsNone(controller.getCurrentSession())

if __name__ == '__main__':
	unittest.main()