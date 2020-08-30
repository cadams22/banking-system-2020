import unittest
import os
import sys
import time

currentDirectory = os.path.dirname(__file__)
relativePath = '../python/'
path = os.path.join(currentDirectory, relativePath)

sys.path.insert(1, path)

from controller import Controller
from readCsvIntoAccounts import ReadCsvIntoAccounts
from session import Session

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

		self.assertEqual(len(controller.getLatestAccountInfo()),4)

	def testLogin(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())

		# check that after login, the user is currently authorized
		self.assertEqual(controller.getCurrentSession().checkAuthorizationStatus(),True)

	def testBalance(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())
		balance = controller.balance()

		# check that the controller is getting the right balance
		self.assertEqual(balance,self.accounts[accountId].getBalance())

	def testTransactionsAfterExpired(self):
		controller = Controller()

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[0]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())
		controller.deposit(value=20)

		# letting authorization expire
		time.sleep(120)

		# testing transactions after timeout
		balance = controller.balance()
		self.assertIsNone(balance)
		transactionHistory = controller.history()
		self.assertIsNone(transactionHistory)
		depositHappened = controller.deposit(value=100)
		self.assertFalse(depositHappened)
		withdrawalHappened = controller.withdraw(value=100)
		self.assertFalse(withdrawalHappened)

	def testDeposit(self):
		value = 1

		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())
		oldBalance = controller.getLatestAccountInfo()[accountId].getBalance()
		controller.deposit(value=value)
		balance = controller.balance()

		# check that after deposit, the balance equals old balance minus one
		self.assertEqual(balance,oldBalance+1)

	def testWithdrawal(self):
		value = 20

		controller = Controller()
		accountId = list(self.accounts.keys())[1]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())
		oldBalance = controller.getLatestAccountInfo()[accountId].getBalance()
		controller.withdraw(value=value)
		balance = controller.getLatestAccountInfo()[accountId].getBalance()

		# check that after deposit, the balance equals old balance minus one
		self.assertEqual(balance,oldBalance-value)

	def testLogout(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.login(accountId=accountId,pin=self.accounts[accountId].getPin())
		controller.deposit(value=20)

		controller.logout()

		balance = controller.balance()
		transactionHistory = controller.history()
		depositHappened = controller.deposit(value=100)
		withdrawalHappened = controller.withdraw(value=100)

		# check that after logout, the user is no longer authorized
		self.assertFalse(controller.getCurrentSession().checkAuthorizationStatus())
		self.assertIsNone(balance)
		self.assertIsNone(transactionHistory)
		self.assertFalse(depositHappened)
		self.assertFalse(withdrawalHappened)

if __name__ == '__main__':
	unittest.main()