#!/usr/bin/python3

import argparse
import getpass
import json
import time
import requests


class Client:
    def __init__(self, server_url="http://127.0.0.1", server_path="/captcha22/api/v1.0/", server_port="5000", username=None, password=None):
        self.username = username
        self.password = password
        self.token = ''
        self.serverURL = f"{server_url}:{server_port}{server_path}"

    def build_token_headers(self):
        headers = {'X-Api-Key': self.token}
        return headers

    def get_token(self):
        url = self.serverURL + "generate_token"
        r = requests.get(url, auth=requests.auth.HTTPBasicAuth(
            self.username, self.password))
        load = json.loads(r.content)
        if load['message'] == 'success':
            print("Got token")
            self.token = load['token']

    def upload_captchas(self, clientName, dataFile):
        url = self.serverURL + "captchas"
        datas = {'title': clientName}
        files = [
            ('document', ("hello", open(dataFile, 'rb'), 'application/octet')),
            ('captcha', ('captcha', json.dumps(datas), 'application/json')),
        ]
        r = requests.post(url, files=files, headers=self.build_token_headers())
        json_data = json.loads(r.content)
        print(json.dumps(json_data, indent=2))

    def get_captcha_details(self, captchaID):
        url = self.serverURL + "captchas/" + str(captchaID)
        r = requests.get(url, headers=self.build_token_headers())
        json_data = json.loads(r.content)
        print(json.dumps(json_data, indent=2))

        return r.content

    def get_captcha_token(self, captchaID):
        load = json.loads(self.get_captcha_details(captchaID))
        token = load['captcha']['dataToken']
        return token

    def get_all_models(self):
        url = self.serverURL + "captchas"
        r = requests.get(url, headers=self.build_token_headers())
        json_data = json.loads(r.content)
        print(json.dumps(json_data, indent=2))

    def get_exported_model(self, captchaID):
        token = self.get_captcha_token(captchaID)
        url = self.serverURL + "export_model/" + token
        r = requests.get(url, headers=self.build_token_headers())

        newFileByteArray = bytearray(r.content)

        newfile = open("exported-model.zip", 'wb')

        newfile.write(newFileByteArray)

    def update_model_active(self, captchaID, answer):
        token = self.get_captcha_token(captchaID)
        url = self.serverURL + "activate_model"
        datas = {
            'active': answer,
            'dataToken': token
        }
        files = [
            ('captcha', ('captcha', json.dumps(datas), 'application/json')),
        ]

        r = requests.post(url, json=datas, headers=self.build_token_headers())
        json_data = json.loads(r.content)
        print(json.dumps(json_data, indent=2))

    def get_training_update(self, captchaID):
        token = self.get_captcha_token(captchaID)
        url = self.serverURL + "training_update/" + token
        r = requests.get(url, headers=self.build_token_headers())
        json_data = json.loads(r.content)
        print(json.dumps(json_data, indent=2))

    def get_results(self, captchaID):
        token = self.get_captcha_token(captchaID)
        url = self.serverURL + "results/" + token
        r = requests.get(url, headers=self.build_token_headers())
        json_data = json.loads(r.content)
        print(json.dumps(json_data, indent=2))

    def solve_captcha(self, captchaID):
        token = self.get_captcha_token(captchaID)
        url = self.serverURL + "solve_captcha"

        import base64

        with open("image.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        datas = {
            'image': encoded_string,
            'dataToken': token
        }
        r = requests.post(url, json=datas, headers=self.build_token_headers())
        json_data = json.loads(r.content)
        print(json.dumps(json_data, indent=2))

class Menu:
    def __init__(self, server_url="http://127.0.0.1", server_path="/captcha22/api/v1.0/", server_port="5000", username=None, password=None):
        self.authed = False

        self.server_url = server_url
        self.server_path = server_path
        self.server_port = server_port
        self.username = username
        self.password = password

    def auth_to_server(self):
        print("[+] Authenticating to Captcha22")
        count = 0
        while(count < 3):
            if self.username == None:
                self.username = str(
                    input("Please provide your username: "))
            if self.password == None:
                self.password = getpass.getpass(
                    'Please provide your password: ')
            self.new_Client = Client(self.server_url, self.server_path, self.server_port, self.username, self.password)
            print("[-] Attempting authentication")
            try:
                self.new_Client.get_token()
            except:
                pass
            if len(self.new_Client.token) > 0:
                print("[-] Authentication successful")
                self.authed = True
                return
            else:
                time.sleep(2)
                print("[x] Invalid credentials, please try again")
                self.username = None
                self.password = None
            count += 1

        print("[x] Attempts failed, please try again")
        exit()

    def upload_captcha_sample(self):
        if (not self.authed):
            self.auth_to_server()
        if (not self.authed):
            return

        print("[+] CAPTCHA upload sequence method called")
        print("[-] Please ensure that the file is a zip file with a subdirectory '/data' containing the labelled CAPTCHA images")
        file_location = str(input("Please provide the file path: "))
        client_name = str(input("Please provide the test name: "))
        print("[-] Uploading file....")
        self.new_Client.upload_captchas(client_name, file_location)
        print("[-] File uploaded")

    def run_exported_model(self):
        print("[X] This method has not yet been implemented")

    def menu_interface(self):
        if (not self.authed):
            self.auth_to_server()
        if (not self.authed):
            return

        print("[+] CAPTCHA22 server interface online. What would you like to do?")
        while(True):
            print("[1] Get details on all CAPTCHA models")
            print("[2] Get details on a CAPTCHA model")
            print("[3] Get the progression of CAPTCHA model training")
            print("[4] Get the results of CAPTCHA model training")
            print("[5] Download a training CAPTHCA model")
            print("[6] Activate a server-side CAPTCHA model")
            print("[7] Cancel")

            answer = str(input("Option: "))
            if (answer == "7"):
                break
            if (answer == "1"):
                self.new_Client.get_all_models()
                continue
            if (answer == "2"):
                captchaID = str(input("Please provide the captchaID: "))
                self.new_Client.get_captcha_details(captchaID)
                continue
            if (answer == "3"):
                captchaID = str(input("Please provide the captchaID: "))
                self.new_Client.get_training_update(captchaID)
                continue
            if (answer == "4"):
                captchaID = str(input("Please provide the captchaID: "))
                self.new_Client.get_results(captchaID)
                continue
            if (answer == "5"):
                captchaID = str(input("Please provide the captchaID: "))
                self.new_Client.get_exported_model(captchaID)
            if (answer == "6"):
                captchaID = str(input("Please provide the captchaID: "))
                status_ask = str(input("Activate? [Y/N]"))
                if (status_ask == "Y" or status_ask == "y"):
                    self.new_Client.update_model_active(captchaID, True)
                else:
                    self.new_Client.update_model_active(captchaID, False)

    def main(self):

        print("[+] Welcome to CAPTCHA22. What would you like to do?")
        while(True):
            print("[1] Upload a CAPTCHA sample")
            print("[2] Run an exported model")
            print("[3] Interface with the Captcha22 server")
            print("[4] Quit")

            answer = str(input("Option: "))
            if (answer == "1"):
                self.upload_captcha_sample()
                print("Connecting to CAPTCHA server")
                continue
            if (answer == "2"):
                self.run_exported_model()
                print("Working with exported model")
                continue
            if (answer == "3"):
                self.menu_interface()
                print("Interfacing with the CAPTCHA22 server")
                continue
            if (answer == "4"):
                break
            print("[x] Invalid option, please try again")


if __name__ == "__main__":

    # Execute
    new_menu = Menu()
    new_menu.main()
