#!/usr/bin/python3

import argparse
import base64
import getpass
import glob
import hashlib
import io
import json
import os
import sys
import time
import requests
import cv2
import numpy as np
from PIL import Image
import logging


class Cracker:
    def __init__(self, server_url="http://127.0.01", server_path="/captcha22/api/v1.0/", server_port="5000", username=None, password=None, session_time=1800, use_hashes=False, use_filter=False, use_local=False, input_dir="./input/", output="./output/", image_type="png", filter_low=130, filter_high=142, captcha_id=None, logger = logging.getLogger("Captcha22 Cracker")):
        self.logger = logger
        # API username and password
        self.username = username
        self.password = password

        self.useLocal = use_local

        if (self.username == None and not self.useLocal):
            self.username = str(input("Please provide your username:"))
        else:
            self.username = username


        if (self.password == None and not self.useLocal):
            self.password = getpass.getpass('Please provide your password:')
        else:
            self.password = password

        self.token = ''

        self.captchaID = captcha_id

        self.server_url = server_url
        self.server_port = server_port
        self.server_path = server_path

        self.useFilter = use_filter
        self.useLocal = use_local

        self.serverURL = self.server_url + ":" + str(self.server_port) + self.server_path

        # Session management var
        self.isActive = False
        self.validSessionTime = int(session_time)
        self.currentSessionTime = 1900

        # Hash collision system
        self.orginal_data_path = input_dir

        try:
            os.mkdir(output)
        except FileExistsError:
            pass

        self.new_data_correct_path = output + "correct/"
        self.new_data_incorrect_path = output + "incorrect/"

        try:
            os.mkdir(self.new_data_correct_path)
        except FileExistsError:
            pass

        try:
            os.mkdir(self.new_data_incorrect_path)
        except FileExistsError:
            pass

        self.tmp_dir = "tmp/"
        try:
            os.mkdir(self.tmp_dir)
        except FileExistsError:
            pass
        self.temp_image_name = "temp.png"

        self.hashes = {}

        self.useHashes = use_hashes

        if (self.useHashes):
            self.load_hashes()
        # Image cleaning system
        self.histRange = np.arange(0, 255)
        self.convertBins = np.arange(0, 255)

        # This filter should be changed to suit your specific captcha. If no filtering is required, simply remove the filter componet
        start = filter_low
        end = filter_high

        while (start <= end):
            self.convertBins[start] = 0
            start += 1

        self.convertBins[254] = 0

        # Captcha feedback and storage system
        self.last_captcha_answer = ""

    def get_captcha_feedback(self, isCorrect):
        if (isCorrect and self.last_captcha_answer != ""):
            # Captcha was correct, save with the last value
            img = cv2.imread(self.tmp_dir + self.temp_image_name)
            cv2.imwrite(self.new_data_correct_path +
                        self.last_captcha_answer + ".png", img)
        else:
            img = cv2.imread(self.tmp_dir + self.temp_image_name)
            cv2.imwrite(self.new_data_incorrect_path +
                        self.last_captcha_answer + ".png", img)
        self.last_captcha_answer = ""

    def load_hashes(self):
        imgFiles = glob.glob(self.orginal_data_path + "*")

        for imgFile in imgFiles:
            hashval = hashlib.md5(open(imgFile, 'rb').read()).hexdigest()
            self.hashes[hashval] = imgFile.replace(
                self.orginal_data_path, '').replace(".png", '')

        imgFile = glob.glob(self.new_data_correct_path + "*")
        for imgFile in imgFiles:
            hashval = hashlib.md5(open(imgFile, 'rb').read()).hexdigest()
            self.hashes[hashval] = imgFile.replace(
                self.orginal_data_path, '').replace(".png", '')

    def compare_hashes(self, imgFile):
        if (not self.useHashes):
            return ""
        hashval = hashlib.md5(open(imgFile, 'rb').read()).hexdigest()
        answer = ""
        try:
            answer = self.hashes[hashval]
        except:
            pass
        return answer

    def add_hash(self, hashval, hashanswer):
        if (not self.useHashes):
            return

        self.hashes[hashval] = hashanswer

    def clean_image(self, imgb64):
        imgdata = base64.b64decode(imgb64)
        image = Image.open(io.BytesIO(imgdata))

        name = self.tmp_dir + self.temp_image_name
        image.save(name)

        if (self.useFilter):
            # Now load and filter the image
            img = cv2.imread(name)

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            hist, bins = np.histogram(gray, bins=self.histRange)

            for bin in self.convertBins:
                gray[np.where(gray == bin)] = 254

            cv2.imwrite(name, gray)

            # Image is now clean

    def check_session_valid(self):
        if (time.time() - self.currentSessionTime > self.validSessionTime):
            self.logger.info("Refreshing Captcha API token")
            self.auth_to_api()

    def auth_to_api(self):
        url = self.serverURL + "generate_token"
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(
            self.username, self.password))
        load = json.loads(r.content)
        if load['message'] == 'success':
            self.logger.info("Got token")
            self.token = load['token']
        self.currentSessionTime = time.time()

    def build_token_headers(self):
        headers = {'X-Api-Key': self.token}
        return headers

    def solve_captcha(self, encoded_string):
        self.check_session_valid()
        if (self.captchaID == None):
            self.captchaID == str(input("Please enter the CAPTCHA ID: "))
        token = self.get_captcha_token(self.captchaID)
        url = self.serverURL + "solve_captcha"

        datas = {
            'image': encoded_string.decode("utf-8"),
            'dataToken': token
        }
        r = requests.post(url, json=datas, headers=self.build_token_headers())
        # Inject code here to talk to Pyppeteer
        json_data = json.loads(r.content)
        self.logger.info(json.dumps(json_data, indent=2))
        return (json_data['outputs']['output'])

    def submit_self(self, b64_image):
        # Build up the json
        data = {
            "signature_name": "serving_default",
            "inputs": {"input": {"b64": b64_image.decode("utf-8")}}
        }
        url = self.serverURL
        r = requests.post(url, json=data)
        buf = r.content
        stuff = buf.decode('utf-8')
        posted_data = json.loads(stuff)
        return (posted_data['outputs']['output'])

    def solve_captcha_b64(self, b64_image):
        # Clean the captcha image
        bimage = b64_image.replace("data:image/png;base64,", "")
        encoded_string = ""
        self.clean_image(bimage)

        if (self.useHashes):
            # Get hash of image, this will be the quick solve method, we also then don't have to store the image
            answer = self.compare_hashes(self.tmp_dir + self.temp_image_name)

            if (answer != ""):
                self.logger.info(
                    "Hash collision, providing the value of the previously seen captcha")
                return answer

        # If we get to this point we are going to have to ask the captcha server for the answer, we should also save this answer so we can get feedback

        # Get ready to solve captcha

        with open(self.tmp_dir + self.temp_image_name, 'rb') as imgtest:
            encoded_string = base64.b64encode(imgtest.read())

        answer = ""
        if (self.useLocal):
            answer = self.submit_self(encoded_string)
        else:
            answer = self.solve_captcha(encoded_string)

        self.last_captcha_answer = answer
        return answer

    def get_captcha_token(self, captchaID):
        load = json.loads(self.get_captcha_details(captchaID))
        token = load['captcha']['dataToken']
        return token

    def get_captcha_details(self, captchaID):
        url = self.serverURL + "captchas/" + str(captchaID)
        r = requests.get(url, headers=self.build_token_headers())
        json_data = json.loads(r.content)
        self.logger.info(json.dumps(json_data, indent=2))
        return r.content

    def main(self):
        path = str(input("Please enter the filepath to your CAPTCHA:"))
        b64_image = base64.b64encode(open(path, 'rb').read()).decode("utf-8")
        self.solve_captcha_b64(b64_image)


if __name__ == "__main__":

    temp_cracker = Cracker()
    temp_cracker.main()
