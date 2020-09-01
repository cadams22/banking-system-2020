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
import utilities

class TestController(unittest.TestCase):
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
		authorizationString = controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		# check that after login, the user is currently authorized
		self.assertEqual(controller.getCurrentSession().checkAuthorizationStatus(),True)
		self.assertEqual(authorizationString,f"{accountId} successfully authorized")

	# attempt to authorize when another user is already authorized
	def testAuthorizeWithFakeId(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		authorizationString = controller.authorize(accountId="potato",pin=self.accounts[accountId].getPin())

		self.assertEqual(authorizationString,"Authorization failed due to invalid accountId")

	# attempt to authorize when another user is already authorized
	def testAuthorizeOverlap(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		authorizationString = controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		accountId = list(self.accounts.keys())[1]
		authorizationString = controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		self.assertEqual(authorizationString,"Another user is already authorized. Please try again later")

	def testBalance(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		balanceString = controller.balance()
		balance = controller.getLatestAccountInfo()[accountId].getBalance()

		# check that the controller is getting the right balance
		self.assertEqual(balance,self.accounts[accountId].getBalance())
		self.assertEqual(balanceString,f"Current balance: {utilities.displayCash(balance)}")

	def testTransactionsEmpty(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		historyText = controller.history()
		self.assertEqual(historyText,"No history found")

	def testTransactions(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		depositValue = 40
		withdrawalValue = 20
		controller.deposit(value=depositValue)
		controller.withdraw(value=withdrawalValue)
		history = controller.history().splitlines()
		self.assertEqual(len(history),2)
		transactionOne = history[0].split(" ")
		transactionTwo = history[1].split(" ")
		# validating that transaction one and two have 4 attributes
		self.assertEqual(len(transactionOne),4)
		self.assertEqual(len(transactionTwo),4)

		# testing withdrawal displays 1st since it's most recent 
		# then testing that the values look as expected
		self.assertEqual(transactionOne[2],utilities.displayCash(-withdrawalValue))
		self.assertEqual(transactionTwo[2],utilities.displayCash(depositValue))

	def testTransactionsAfterExpired(self):
		controller = Controller()

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		controller.deposit(value=20)

		# letting authorization expire
		time.sleep(120)

		# testing transactions after timeout
		self.assertFalse(controller.getCurrentSession().checkAuthorizationStatus())
		authorizationReqString = "Authorization required."
		balanceString = controller.balance()
		self.assertEqual(balanceString,authorizationReqString)
		transactionString = controller.history()
		self.assertEqual(transactionString,authorizationReqString)
		depositString = controller.deposit(value=100)
		self.assertEqual(depositString,authorizationReqString)
		withdrawalString = controller.withdraw(value=100)
		self.assertEqual(withdrawalString,authorizationReqString)

	def testWithdrawalNotMultipleOf20(self):
		controller = Controller()

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[3]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		withdrawalString = controller.withdraw(value=101)
		self.assertEqual(withdrawalString,"Withdrawal amount must be a multiple of $20")

	def testWithdrawalZero(self):
		controller = Controller()

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[3]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		withdrawalString = controller.withdraw(value=0)
		self.assertEqual(withdrawalString,"Please request a withdrawal of a non-zero amount of money")

	def testWithdrawalNegative(self):
		controller = Controller()

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[3]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		withdrawalString = controller.withdraw(value=-1)
		self.assertEqual(withdrawalString,"You must request a withdrawal a value greater than 0")

	def testOverdrafts(self):
		controller = Controller()

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[3]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		balance = controller.getLatestAccountInfo()[accountId].getBalance()
		# overdrafting test
		value = 100
		withdrawalString = controller.withdraw(value=value)
		expectedBalance = balance-value-5
		expected = f"Amount dispensed: ${utilities.displayCash(value)}\n" + f"You have been charged an overdraft fee of $5. Current balance: {utilities.displayCash(expectedBalance)}"
		self.assertEqual(withdrawalString,expected)

		# controller should prevent the user from withdrawing from an overdrafted account
		value = 100
		withdrawalString = controller.withdraw(value=value)
		self.assertEqual(withdrawalString,"Your account is overdrawn! You may not make withdrawals at this time.")

		# but when we deposit money to make the account balance positive
		# the account should no longer be overdrafted
		# and a subsequent withdrawal should occur successfully
		value = 100
		controller.deposit(value=value)
		withdrawalString = controller.withdraw(value=value)
		# expectedBalance = expectedBalance + deposit - withdrawal -5 becomes expectedBalance - 5 since deposit=withdrawal
		expectedBalance = expectedBalance - 5
		expected = f"Amount dispensed: ${utilities.displayCash(value)}\n" + f"You have been charged an overdraft fee of $5. Current balance: {utilities.displayCash(expectedBalance)}"
		self.assertEqual(withdrawalString,expected)

	def testEmptyAtm(self):
		cash = 10000
		controller = Controller(startingCash=cash)

		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[1]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())

		oldBalance = controller.getLatestAccountInfo()[accountId].getBalance()
		withdrawalString = controller.withdraw(value=cash+20)
		# i expect the ATM dispensed the amount of money in the ATM equal to cash, not cash+20
		expected = "Unable to dispense full amount requested at this time.\n" + f"Amount dispensed: ${utilities.displayCash(cash)}\n" + controller.balance()
		self.assertEqual(withdrawalString,expected)
		self.assertEqual(controller.getLatestAccountInfo()[accountId].getBalance(),oldBalance-cash)

		# controller should prevent the user from withdrawing from an overdrafted account
		value=100
		withdrawalString = controller.withdraw(value=value)
		self.assertEqual(withdrawalString,"Unable to process your withdrawal at this time.")

		# but when we deposit money to make the atm have cash=1000
		# the atm should be able to withdraw the rest of the money
		value=100
		controller.deposit(value=value)
		withdrawalString = controller.withdraw(value=value)
		# validating $100 was withdrawn after $100 was added to the empty ATM
		self.assertEqual(withdrawalString,f"Amount dispensed: ${utilities.displayCash(value)}\n" + controller.balance())

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

		# testing transactions after timeout
		self.assertFalse(controller.getCurrentSession().checkAuthorizationStatus())
		authorizationReqString = "Authorization required."
		balanceString = controller.balance()
		self.assertEqual(balanceString,authorizationReqString)
		transactionString = controller.history()
		self.assertEqual(transactionString,authorizationReqString)
		depositString = controller.deposit(value=100)
		self.assertEqual(depositString,authorizationReqString)
		withdrawalString = controller.withdraw(value=100)
		self.assertEqual(withdrawalString,authorizationReqString)

	def testSwitchingBetweenAccounts(self):
		controller = Controller()
		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		oldBalance = controller.getLatestAccountInfo()[accountId].getBalance()
		depositValue = 40
		withdrawalValue = 20
		controller.deposit(value=depositValue)
		controller.withdraw(value=withdrawalValue)
		newBalance = oldBalance + depositValue - withdrawalValue
		balanceString = controller.balance()
		self.assertEqual(balanceString,f"Current balance: {utilities.displayCash(newBalance)}")
		history = controller.history().splitlines()
		self.assertEqual(len(history),2)
		controller.logout()

		accountId = list(self.accounts.keys())[1]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		beforeBalance = controller.getLatestAccountInfo()[accountId].getBalance()
		controller.deposit(value=depositValue)
		controller.withdraw(value=withdrawalValue)
		balanceString = controller.balance()
		expectedBalance = beforeBalance + depositValue - withdrawalValue
		self.assertEqual(balanceString,f"Current balance: {utilities.displayCash(expectedBalance)}")
		history = controller.history().splitlines()
		self.assertEqual(len(history),2)
		controller.logout()

		accountId = list(self.accounts.keys())[0]
		controller.authorize(accountId=accountId,pin=self.accounts[accountId].getPin())
		balanceString = controller.balance()
		self.assertEqual(balanceString,f"Current balance: {utilities.displayCash(oldBalance + depositValue - withdrawalValue)}")

if __name__ == '__main__':
	unittest.main()
