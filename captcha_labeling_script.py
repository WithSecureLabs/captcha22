#!/usr/bin/python
import glob
import cv2
import sys
import os

def label_captchas(read_dir, write_dir):
	#Reading files
	onlyfiles = glob.glob(read_dir + "*")

	#Iterate through files. All keys accepted. Press "-" to finish CAPTCHA label. Press "`" to exit program
	for o in onlyfiles:    
	    if(o.find("png")!=-1):
		img = cv2.imread(o)
		print "Showing image"
		text = ''
		while(1):
			cv2.imshow('captcha', img)
			c = cv2.waitKey(0)
			if c==ord('-'):
				print "Exiting"
				break
			elif c==ord('`'):
				print "Full exit"
				exit()
			else:
				print 'you pressed %s' % chr(c)
				text += chr(c)

		print "Final text is: ", text
		save_name = write_dir + text.upper() + '.png'

		#Save the image
		cv2.imwrite(write_dir + text.upper() + '.png', img)
		#Remove the old image
		os.remove(o)

if __name__ == "__main__":
	print "Usage: ./captcha_labeling_script.py <directory with CAPTCHAs> <directory to store labeled CAPTCHAs>"
	print "Enter the label for the CAPTCHA. Use \"-\" to terminate entry and \"`\" to quit."
	try:
		read_dir = sys.argv[1]
		write_dir = sys.argv[2]
		label_captchas(read_dir, write_dir)
	except:
		print "Please provide the directory where the CAPTCHAs are stored as well as the directory to store the labelled CAPTCHAs in."

	


