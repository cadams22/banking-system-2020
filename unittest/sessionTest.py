import unittest
import os
import sys

currentDirectory = os.path.dirname(__file__)
relativePath = '../python/'
path = os.path.join(currentDirectory, relativePath)

sys.path.insert(1, path)

from session import Session
from csvReader import CsvReader
from atm import Atm

class TestSession(unittest.TestCase):

	def setUp(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		relativePath = "csvtest/"
		self.path = os.path.abspath(os.path.join(dir_path, relativePath))

		csvReader = CsvReader(filename='/bankingInfoSample.csv',path=self.path)
		df = csvReader.readCsvIntoDf()
		self.accounts = csvReader.createAccountsUsingDf(df)

	# at the start of the session, the authorization time should be none and authorization status should be 0
	# 0 represents no user currently logged in
	def testAuthorizationTimeAtStart(self):
		testSession = Session()
		self.assertEqual(testSession.checkAuthorizationStatus(),False)

	# check authorization after login - this should return 1 - yes, the user is currently authorized
	def testAuthorizationTimeAfterLogin(self):
		testSession = Session()
		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[0]
		authorized = testSession.authorize(accountId=accountId,pin=self.accounts[accountId].getPin(),accounts=self.accounts)

		# check that the function returns True, meaning authorization was successful
		self.assertEqual(authorized,True)

		# check that after login, the user is currently authorized
		self.assertEqual(testSession.checkAuthorizationStatus(),authorized)

	# check authorization fails if the user provides the wrong pin
	def testFailedAuthorization(self):
		testSession = Session()
		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[0]
		# adding 1 to the actual pin. For example, 7386 becomes 7387
		authorized = testSession.authorize(accountId=accountId,pin=self.accounts[accountId].getPin()+1,accounts=self.accounts)
		# check that the function returns False, meaning authorization failed
		self.assertEqual(authorized,False)

		# check that after that failed login, the user is currently not authorized
		self.assertEqual(testSession.checkAuthorizationStatus(),authorized)
		
	def testGetBalance(self):
		testSession = Session()
		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[0]
		testSession.authorize(accountId=accountId,pin=self.accounts[accountId].getPin(),accounts=self.accounts)

		self.assertEqual(testSession.getBalance(self.accounts),self.accounts[accountId].getBalance())

	def testDeposit(self):
		value = 1
		atm = Atm()

		testSession = Session()
		accountId = list(self.accounts.keys())[0]
		testSession.authorize(accounts=self.accounts,accountId=accountId,pin=self.accounts[accountId].getPin())
		oldBalance = self.accounts[accountId].getBalance()
		testSession.deposit(accounts=self.accounts,atm=atm,value=value)
		balance = testSession.getBalance(accounts=self.accounts)

		# check that after deposit, the return value equals the passed-in value. this means the deposit was successful
		self.assertEqual(balance,oldBalance+value)

	def testWithdrawal(self):
		value = 20
		atm = Atm()

		testSession = Session()
		accountId = list(self.accounts.keys())[3]
		testSession.authorize(accounts=self.accounts,accountId=accountId,pin=self.accounts[accountId].getPin())
		returnValue = testSession.withdraw(accounts=self.accounts,atm=atm,value=value)
		balance = testSession.getBalance(accounts=self.accounts)

		# check that after withdrawal, the balance equals old balance minus value
		self.assertEqual(returnValue,value)

	def testWithdrawalOverdraft(self):
		value = 100
		atm = Atm()

		testSession = Session()
		accountId = list(self.accounts.keys())[0]
		testSession.authorize(accounts=self.accounts,accountId=accountId,pin=self.accounts[accountId].getPin())
		oldBalance = testSession.getBalance(accounts=self.accounts)
		returnValue = testSession.withdraw(accounts=self.accounts,atm=atm,value=value)
		balance = testSession.getBalance(accounts=self.accounts)

		# check that after withdrawal, the balance equals old balance minus value minus $5 overdraft fee
		self.assertEqual(returnValue,value)
		self.assertEqual(balance,oldBalance-value-5)
		# account should be overdrawn
		self.assertTrue(self.accounts[testSession.getCurrentAccountId()].getOverdrawnStatus())



if __name__ == '__main__':
	unittest.main()