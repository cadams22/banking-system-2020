import unittest
import os
import sys
import time

currentDirectory = os.path.dirname(__file__)
relativePath = '../python/'
path = os.path.join(currentDirectory, relativePath)

sys.path.insert(1, path)

from session import Session
from readCsvIntoAccounts import ReadCsvIntoAccounts

class TestReadCsvIntoAccounts(unittest.TestCase):

	def setUp(self):
		classObject = ReadCsvIntoAccounts(filename='bankingInfoSample.csv',relativePath='../unittest/csvtest/')
		df = classObject.readCsvIntoDf()
		self.accounts = classObject.createAccountsUsingDf(df)

	# at the start of the session, the authorization time should be none and authorization status should be 0
	# 0 represents no user currently logged in
	def testAuthorizationTimeAtStart(self):
		testSession = Session()
		self.assertEqual(testSession.checkAuthorizationStatus(),0)

	# check authorization after login - this should return 1 - yes, the user is currently authorized
	def testAuthorizationTimeAfterLogin(self):
		testSession = Session()
		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[0]
		testSession.authorize(accountId=accountId,pin=self.accounts[accountId].getPin(),accounts=self.accounts)

		# check that after login, the user is currently authorized
		self.assertEqual(testSession.checkAuthorizationStatus(),1)
		# check that after login, the user is currently authorized when we manually pass in accountId
		self.assertEqual(testSession.checkAuthorizationStatus(accountId=accountId),1)
		# check that for another arbitrary account, this returns 2, another user is authorized
		self.assertEqual(testSession.checkAuthorizationStatus(accountId=-9999),2)
		
	def testGetBalance(self):
		testSession = Session()
		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[0]
		testSession.authorize(accountId=accountId,pin=self.accounts[accountId].getPin(),accounts=self.accounts)

		self.assertEqual(testSession.getBalance(self.accounts),self.accounts[accountId].getBalance())

	def testGetBalanceAfterExpired(self):
		balance = None

		testSession = Session()
		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[0]
		testSession.authorize(accountId=accountId,pin=self.accounts[accountId].getPin(),accounts=self.accounts)

		# letting authorization expire
		time.sleep(120)

		balance = testSession.getBalance(self.accounts)
		self.assertIsNone(balance)



if __name__ == '__main__':
	unittest.main()