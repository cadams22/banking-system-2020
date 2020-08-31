import unittest
import sys
import os
import pandas as pd

currentDirectory = os.path.dirname(__file__)
relativePath = '../python/'
path = os.path.join(currentDirectory, relativePath)

sys.path.insert(1, path)

from csvReader import CsvReader

class TestCsvReader(unittest.TestCase):

	def setUp(self):
		dir_path = os.path.dirname(os.path.realpath(__file__))
		relativePath = "csvtest/"
		self.path = os.path.abspath(os.path.join(dir_path, relativePath))

	# testing a file with just headers
	def testHeadersCsv(self):
		csvReader = CsvReader(filename='/headers.csv',path=self.path)

		df = csvReader.readCsvIntoDf()

		#making sure there are no errors and an empty dataframe is created
		self.assertEqual(len(df),0)

		dictionary = csvReader.createAccountsUsingDf(df)
		#making sure there are no errors and an empty dictionary of account info is created
		self.assertEqual(len(dictionary),0)

	# testing an empty file 
	# negative test: this should cause an EmptyDataError to be raised
	def testEmptyCsv(self):
		csvReader = CsvReader(filename='/empty.csv',path=self.path)

		self.assertRaises(pd.errors.EmptyDataError, csvReader.readCsvIntoDf)

	# testing the csv sent to me
	def testBankingInfoSampleCsv(self):
		csvReader = CsvReader(filename='/bankingInfoSample.csv',path=self.path)

		df = csvReader.readCsvIntoDf()

		#we have 4 accounts in the CSV file
		self.assertEqual(len(df),4)

		dictionary = csvReader.createAccountsUsingDf(df)
		#making sure there are no errors and an empty dictionary of account info is created
		self.assertEqual(len(dictionary),4)

if __name__ == '__main__':
	unittest.main()