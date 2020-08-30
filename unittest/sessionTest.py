import unittest
import os
import sys

currentDirectory = os.path.dirname(__file__)
relativePath = '../python/'
path = os.path.join(currentDirectory, relativePath)

sys.path.insert(1, path)

from session import Session
from readCsvIntoAccounts import ReadCsvIntoAccounts

class TestSession(unittest.TestCase):

	def setUp(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		relativePath = "csvtest/"
		self.path = os.path.abspath(os.path.join(dir_path, relativePath))

		classObject = ReadCsvIntoAccounts(filename='/bankingInfoSample.csv',path=self.path)
		df = classObject.readCsvIntoDf()
		self.accounts = classObject.createAccountsUsingDf(df)

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
		testSession.authorize(accountId=accountId,pin=self.accounts[accountId].getPin(),accounts=self.accounts)

		# check that after login, the user is currently authorized
		self.assertEqual(testSession.checkAuthorizationStatus(),True)
		
	def testGetBalance(self):
		testSession = Session()
		# get first item in the accounts dictionary
		accountId = list(self.accounts.keys())[0]
		testSession.authorize(accountId=accountId,pin=self.accounts[accountId].getPin(),accounts=self.accounts)

		self.assertEqual(testSession.getBalance(self.accounts),self.accounts[accountId].getBalance())



if __name__ == '__main__':
	unittest.main()