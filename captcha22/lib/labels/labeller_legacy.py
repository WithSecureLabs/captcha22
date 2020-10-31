#!/usr/bin/python3

import argparse
import glob
import os
import sys
import cv2
import logging

class CaptchaLabeller:
    def __init__(self, input_dir="input/", output="output/", image_type="png", logger = logging.getLogger("Captcha22 Captcha Labeller")):
        self.logger = logger
        self.read_dir = input_idr
        self.write_dir = output
        self.image_type = image_type

    def label_captchas(self):
        # Reading files
        onlyfiles = glob.glob(self.read_dir + "*")

        # Iterate through files. All keys accepted. Press "-" to finish CAPTCHA label. Press "`" to exit program
        for o in onlyfiles:
            if(o.find(self.image_type) != -1):
                img = cv2.imread(o)
                self.logger.info("Showing image")
                text = ''
                while(1):
                    cv2.imshow('captcha', img)
                    c = cv2.waitKey(0)
                    if c == ord('-'):
                        self.logger.info("Exiting")
                        break
                    elif c == ord('`'):
                        self.logger.info("Full exit")
                        exit()
                    else:
                        self.logger.info('you pressed %s' % chr(c))
                        text += chr(c)

                self.logger.info("Final text is: " + text)

                # Save the image
                cv2.imwrite(self.write_dir + text.upper() +
                            '.' + self.image_type, img)
                # Remove the old image
                os.remove(o)

    def main(self):
        self.label_captchas()


if __name__ == "__main__":
    labeller = CaptchaLabeller()

    labeller.main()
