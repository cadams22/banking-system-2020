import unittest
import os
import sys
import time

currentDirectory = os.path.dirname(__file__)
relativePath = '../python/'
path = os.path.join(currentDirectory, relativePath)

sys.path.insert(1, path)

from controller import Controller
from csvReader import CsvReader
from session import Session

class TestController(unittest.TestCase):
	#todo: enhance by adding tests to validate the returned strings
	def setUp(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		relativePath = "../csv/"
		self.path = os.path.abspath(os.path.join(dir_path, relativePath))

		csvReader = CsvReader(filename='/bankingInfo.csv',path=self.path)
		df = csvReader.readCsvIntoDf()
		self.accounts = csvReader.createAccountsUsingDf(df)

	def testInit(self):
		controller = Controller()

		self.assertEqual(len(controller.getLatestAccountInfo()),4)

	def testAuthorize(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		# check that after login, the user is currently authorized
		self.assertEqual(controller.getCurrentSession().checkAuthorizationStatus(),True)

	def testBalance(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		balance = controller.balance()

		# check that the controller is getting the right balance
		self.assertEqual(balance,self.accounts[accountId].getBalance())

	def testTransactionsAfterExpired(self):
		controller = Controller()

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
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

	def testWithdrawlNotMultipleOf20(self):
		controller = Controller()

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[3]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		withdrawalHappened = controller.withdraw(value=101)
		self.assertFalse(withdrawalHappened)

	def testOverdrafts(self):
		controller = Controller()

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[3]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		withdrawalHappened = controller.withdraw(value=100)
		self.assertTrue(withdrawalHappened)

		# controller should prevent the user from withdrawing from an overdrafted account
		withdrawalHappened = controller.withdraw(value=100)
		self.assertFalse(withdrawalHappened)

		# but when we deposit money to make the account balance positive
		# the account should no longer be overdrafted
		# and a subsequent withdrawal should occur successfully
		controller.deposit(value=100)
		withdrawalHappened = controller.withdraw(value=100)
		self.assertTrue(withdrawalHappened)

	def testEmptyAtm(self):
		cash = 10000
		controller = Controller(startingCash=cash)

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[1]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		oldBalance = controller.balance()
		withdrawalHappened = controller.withdraw(value=cash+20)
		self.assertTrue(withdrawalHappened)
		self.assertEqual(controller.balance(),oldBalance-cash)

		# controller should prevent the user from withdrawing from an overdrafted account
		withdrawalHappened = controller.withdraw(value=100)
		self.assertFalse(withdrawalHappened)

		# but when we deposit money to make the atm have cash=1000
		# the atm should be able to withdraw the rest of the money
		controller.deposit(value=100)
		withdrawalHappened = controller.withdraw(value=100)
		self.assertTrue(withdrawalHappened)

	def testLogout(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
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

	def testSwitchingBetweenAccounts(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		oldBalance = controller.balance()
		depositValue = 40
		withdrawalValue = 20
		controller.deposit(value=depositValue)
		controller.withdraw(value=withdrawalValue)
		newBalance = oldBalance + depositValue - withdrawalValue
		balance = controller.balance()
		self.assertEqual(balance,newBalance)
		history = controller.history()
		self.assertEqual(len(history),2)
		controller.logout()

		accountId = list(self.accounts.keys())[1]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		beforeBalance = controller.balance()
		controller.deposit(value=depositValue)
		controller.withdraw(value=withdrawalValue)
		balance = controller.balance()
		self.assertEqual(balance,beforeBalance + depositValue - withdrawalValue)
		history = controller.history()
		self.assertEqual(len(history),2)
		controller.logout()

		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		balance = controller.balance()
		self.assertEqual(balance,oldBalance + depositValue - withdrawalValue)

if __name__ == '__main__':
	unittest.main()
