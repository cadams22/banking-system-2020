# using the pandas library to read the csv file into a dataframe
import os
import pandas as pd

def readCsv(relativePath,filename): 
	# making sure we get the full path to this current file
	# just doing ../csv causes problems when you run this script from a different directory
	currentDirectory = os.path.dirname(__file__)

	# i keep the csv in path ../csv/ relative to the location of this script
	path = os.path.join(currentDirectory, relativePath)
	# full path for the csv
	fileWithPath = path + filename

	# dataframe of banking info
	# specifying that the first line of this file is a header
	df = pd.read_csv(fileWithPath)

	return df