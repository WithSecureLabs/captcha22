#!/usr/bin/python3
import glob
import sys
import argparse
import logging


class LabelGenerator:
    def __init__(self, input_dir="input/", output="output/", image_type="png", logger = logging.getLogger("Captcha22 Label Generator")):
        self.logger = logger
        self.read_dir = input_dir
        self.write_dir = output
        self.image_type = image_type

    def create_labels(self):
        # Reading files
        onlyfiles = glob.glob(f"{self.read_dir}*.{self.image_type}")

        # Label file
        labels = open(f"{self.write_dir}labels.txt", "w")

        # Create the labels
        for file in onlyfiles:
            answer = file.replace("." + self.image_type, '').split('/')[-1].split('_')[-1]
            labels.write(file.split('/')[-1] + ' ' + answer + '\n')
        labels.close()

    def main(self):
        self.create_labels()


if __name__ == "__main__":

    # Startup
    generator = LabelGenerator()
    generator.main()
