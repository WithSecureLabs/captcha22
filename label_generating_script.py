#!/usr/bin/python
import glob
import sys

def create_labels(read_dir, write_dir):
	#Reading files
	onlyfiles = glob.glob(read_dir + "*.png")

	#Label file
	labels = open(write_dir + "labels.txt", "w")

	#Create the labels
	for file in onlyfiles:
		answer = file.replace('.png','').split('/')[-1]
		labels.write(file.split('/')[-1] + ' ' + answer + '\n')

	labels.close()

if __name__ == "__main__":
	print "Usage: ./label_generating_script.py <directory where CAPTCHAs are stored> <directory to store label file>"
	try:
		read_dir = sys.argv[1]
		write_dir = sys.argv[2]
		create_labels(read_dir, write_dir)
	except:
		print "Please provide the directory where the labelled CAPTCHAs are stored as well as the directory to store the label file in"
