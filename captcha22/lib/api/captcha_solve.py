#!/usr/bin/python3

import argparse
import getpass
import glob
import json
import time
import requests
import cv2
import logging


class Client:
    def __init__(self, server_url="http://127.0.0.1", server_path="/captcha22/api/v1.0/", server_port="5000", input_dir="./input/", image_type="png", captcha_id=None, username=None, password=None, logger = logging.getLogger("Captcha22 Client API")):

        self.logger = logger

        self.username = username
        self.password = password
        self.token = ''
        self.serverURL = server_url + ":" + server_port + server_path

    def build_token_headers(self):
        headers = {'X-Api-Key': self.token}
        return headers

    def get_token(self):
        url = self.serverURL + "generate_token"
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(
            self.username, self.password))
        load = json.loads(r.content)
        if load['message'] == 'success':
            self.logger.info("Got token")
            self.token = load['token']

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

    def solve_captcha(self, captchaID):
        token = self.get_captcha_token(captchaID)
        url = self.serverURL + "solve_captcha"

        import base64
        # This solver expects the images in a directory. Alter or request this if you use something else.
        image_path = "images/"
        images = glob.glob(image_path + "*.png")

        for image in images:
            with open(image, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())
                datas = {
                    'image': encoded_string.decode("utf-8"),
                    'dataToken': token
                }
                r = requests.post(
                    url, json=datas, headers=self.build_token_headers())
                json_data = json.loads(r.content)
                self.logger.info(json.dumps(json_data, indent=2))
                img = cv2.imread(image)
                cv2.imshow('captcha', img)
                c = cv2.waitKey(0)


class Menu:
    def __init__(self, server_url="http://127.0.0.1", server_path="/captcha22/api/v1.0/", server_port="5000", input_dir="./input/", image_type="png", captcha_id=None, username=None, password=None, logger = logging.getLogger("Captcha22 Client API")):
        self.logger = logger
        self.authed = False
        self.username = username
        self.password = password


        self.server_url = server_url
        self.server_path = server_path
        self.server_port = server_port
        self.input_dir = input_dir
        self.image_type = image_type
        self.captcha_id = captcha_id

    def auth_to_server(self):
        self.logger.info("[+] Authenticating to Captcha22")
        count = 0
        while(count < 3):
            if (self.username == None):
                self.username = str(
                    input("Please provide your username: "))
            if (self.password == None):
                self.password = getpass.getpass(
                    'Please provide your password: ')
            self.new_Client = Client(self.server_url, self.server_path, self.server_port, self.input_dir, self.image_type, self.captcha_id, self.username, self.password, self.logger)
            self.logger.info("[-] Attempting authentication")
            try:
                self.new_Client.get_token()
            except:
                pass
            if len(self.new_Client.token) > 0:
                self.logger.info("[-] Authentication successful")
                self.authed = True
                return
            else:
                time.sleep(2)
                self.username = None
                self.password = None
                self.logger.info("[x] Invalid credentials, please try again")
            count += 1

        self.logger.info("[x] Attempts failed, please try again")
        exit()

    def solve(self):
        self.logger.info("[+] Starting CAPTCHA Solving System")
        if (not self.authed):
            self.auth_to_server()
        if (not self.authed):
            return

        if (self.captcha_id == None):
            self.captcha_id = str(input("Please provide the CAPTCHA ID: "))

        self.new_Client.solve_captcha(self.captcha_id)

    def main(self):
        self.solve()

    def menu_run(self):

        self.logger.info("[+] Welcome to Captcha22. What would you like to do?")
        while(True):
            self.logger.info("[1] Run Solution")
            self.logger.info("[2] Quit")

            answer = str(input("Option: "))
            if (answer == "1"):
                self.solve()
                continue
            if (answer == "2"):
                break
            self.logger.info("[x] Invalid option, please try again")


if __name__ == "__main__":
    # Execute
    new_menu = Menu()
    new_menu.main()
