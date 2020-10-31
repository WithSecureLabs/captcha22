#!/usr/bin/python3

import argparse
import os
import ast
import glob
import json
import random
import shutil
import string
import time
import uuid
import requests
import logging
from flask import Flask, abort, jsonify, make_response, request, send_file
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_restful import Api, Resource, fields, marshal, reqparse
from werkzeug.security import check_password_hash, generate_password_hash
from flask_cors import CORS

class user:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.tokens = {}


class AuthSystem:
    def __init__(self, source):
        self.auth = HTTPBasicAuth()

        self.source = source

        @self.auth.verify_password
        def verify_password(username, password):
            for user in self.source.users:
                if user.username == username:
                    return check_password_hash(user.password, password)
            return False

        @self.auth.error_handler
        def unauthorized():
            # return 403 instead of 401 to prevent browsers from displaying the default
            # auth dialog
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)

        self.second_auth = HTTPTokenAuth()

        @self.second_auth.verify_token
        def verify_token(token):
            self.clean_tokens()
            headers = request.headers
            token = headers.get("X-Api-Key")
            for user in self.source.users:
                for current_token in user.tokens:
                    if user.tokens[current_token][0] == token:
                        return True
            return False

        @self.second_auth.error_handler
        def unauthorized():
            # return 403 instead of 401 to prevent browsers from displaying the default
            # auth dialog
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)

    def verify_connect(self):
        username = request.authorization["username"]
        password = request.authorization["password"]

        for user in self.source.users:
            if user.username == username:
                return check_password_hash(user.password, password)
        return False

    def clean_tokens(self):
        max_time = 3600
        current_time = time.time()
        for user in self.source.users:
            tokens_delete = []
            for current_token in user.tokens:
                if (current_time - user.tokens[current_token][1]) > max_time:
                    tokens_delete.append(current_token)

            for deletion in tokens_delete:
                del user.tokens[current_token]

    def get_username(self):
        headers = request.headers
        token = headers.get("X-Api-Key")
        for user in self.source.users:
            for current_token in user.tokens:
                if user.tokens[current_token][0] == token:
                    return user.username
        return ""

    def verify_token(self, token):
        for user in self.source.users:
            for current_token in user.tokens:
                if user.tokens[current_token][0] == token:
                    return True
        return False

    def get_and_verify(self):
        self.source.logger.info("verifying token")
        # First make sure there are no old tokens
        self.clean_tokens()
        headers = request.headers
        token = headers.get("X-Api-Key")
        return self.verify_token(token)


class data_source:
    def __init__(self, file_drop="./Unsorted/", max_tokens=5, server_location="./", user_file="users.txt", work_folder="./Busy", model_folder="./Model", logger = logging.getLogger("Captcha22 API Data Source")):

        self.logger = logger

        self.FILE_DROP_LOCATION = file_drop
        self.CAPTCHA_SERVER_LOCATION = server_location
        self.MODELS = model_folder + "/"
        self.WORK = work_folder + "/"

        self.max_tokens = max_tokens
        self.users = []
        self.user_file = user_file
        lines = []
        try:
            f = open(self.user_file)
            lines = f.readlines()
        except:
            f = open(self.user_file, 'w')
            f.write('admin' + ',' + generate_password_hash('admin') + "\n")
            lines.append('admin' + ',' + generate_password_hash('admin') + "\n")
            f.close()
            pass

        for line in lines:
            userData = line.replace("\n", "").split(',')

            try:
                self.users.append(user(userData[0], userData[1]))
            except:
                pass

        # Now get the captchas
        self.captcha_fields = {
            'title': fields.String,
            'username': fields.String,
            'modelNumber': fields.Integer,
            'dataToken': fields.String,
            'busyTraining': fields.Boolean,
            'hasModel': fields.Boolean,
            'modelActive': fields.Boolean,
            'uri': fields.Url('captcha')
        }

        self.solution_fields = {
            'output': fields.String,
            'probability': fields.Float,
            'error': fields.String
        }

        self.training_progress_fields = {
            'captcha': self.captcha_fields,
            'currentTrainingLevel': fields.String,
            'last_step': fields.String,
            'loss': fields.String,
            'perplexity': fields.String,
            'checkpoint': fields.String,
        }

        self.results_fields = {
            'correct': fields.Integer,
            'totalPredictions': fields.Integer,
            'accuracy': fields.String,
            'wrong_answers': fields.String,
        }

        self.captchas = []
        # Start building the captchas
        count = 1
        for test_user in self.users:
            # Navigate through the files and find the captcha files, remember to generate UIDs for them
            dirs = glob.glob(self.WORK + test_user.username + "/*")
            for dir in dirs:
                client = dir.split('/')[-1]
                model_numbers = glob.glob(dir + "/*")
                for number in model_numbers:
                    number_model = number.split('/')[-1]
                    # In each of these we can pull config from the current file structure.
                    # retrieve data from captcha here:
                    update = self.get_update(number)
                    captcha = {
                        'id': count,
                        'title': str(client),
                        'username': str(test_user.username),
                        'modelNumber': int(number_model),
                        'dataToken': str(uuid.uuid1()),
                        'busyTraining': False,
                        'hasModel': False,
                        'modelActive': False
                    }
                    try:
                        captcha['busyTraining'] = update['busyTraining']
                        captcha['hasModel'] = update['hasModel']
                        captcha['modelActive'] = update['modelActive']
                    except:
                        pass
                    self.captchas.append(captcha)
                    count += 1

    def registerUser(self, username, password):
        #First test to make sure the username and password are not empty
        if (len(username) < 1 or len(password) < 1):
            return False
        #Now we can ensure that the user does not exist already
        for myuser in self.users:
            if (myuser.username == username):
                return False

        #Now we can test our password policy - our password policy only requires the password to be 16 character long, no complexity. This is to make a push passphrases
        if (len(password) < 16):
            return False

        #All checks out, now we can add the user
        self.users.append(user(username, generate_password_hash(password)))

        f = open(self.user_file, 'w')
        for myuser in self.users:
            f.write(myuser.username + "," + myuser.password + "\n")
        f.close()
        return True

    def change_model_status(self, captcha, status):
        self.logger.info("Status is now: " + str(status))
        file_location = self.WORK + captcha['username'].replace(
            " ", "") + "/" + captcha['title'].replace(" ", "") + "/" + str(captcha['modelNumber'])
        update = self.get_update(file_location)
        if update['modelOn'] == status:
            return

        try:
            f = open(file_location + "/model.txt", 'w')
            f.write(str(update['hasTrained']) + "\n")
            f.write(str(update['busyTraining']) + "\n")
            f.write(str(update['hasModel']) + "\n")
            f.write(str(update['modelActive']) + "\n")
            f.write(str(update['modelPorts']) + "\n")
            f.write(str(update['currentTrainingLevel']) + "\n")
            f.write(str(update['image_width']) + "\n")
            f.write(str(update['image_height']) + "\n")
            f.write(str(update['last_step']) + "\n")
            f.write(str(update['loss']) + "\n")
            f.write(str(update['perplexity']) + "\n")
            f.write(str(update['checkpoint']) + "\n")
            f.write(str(update['modelName']) + "\n")
            f.write(str(update['modelPath']) + "\n")
            f.write(str(status) + "\n")
            f.close()

        except:
            pass

    def get_captcha_solution(self, captcha, image):
        file_location = self.WORK + captcha['username'].replace(
            " ", "") + "/" + captcha['title'].replace(" ", "") + "/" + str(captcha['modelNumber'])
        update = self.get_update(file_location)
        if update['modelActive'] == False:
            return {'error': "The Model is currently not being served. Please enable the model first"}

        # Build up the json
        data = {
            "signature_name": "serving_default",
            "inputs": {"input": {"b64": image}}
        }
        # Captcha server hosts the models locally. IP is therefore hard fixed. Please change this is you use the API on another host
        url = "http://127.0.0.1:" + \
            str(update['modelPorts'] + 1) + "/v1/models/" + \
            str(update['modelName']) + ":predict"
        r = requests.post(url, json=data)
        buf = r.content
        stuff = buf.decode('utf-8')
        posted_data = json.loads(stuff)
        return (posted_data['outputs'])

    def get_update(self, folder):
        update = {}
        try:
            f = open(folder + "/model.txt")
            lines = f.readlines()
            update['hasTrained'] = ast.literal_eval(lines[0].replace("\n", ""))
            update['busyTraining'] = ast.literal_eval(
                lines[1].replace("\n", ""))
            update['hasModel'] = ast.literal_eval(lines[2].replace("\n", ""))
            update['modelActive'] = ast.literal_eval(
                lines[3].replace("\n", ""))
            update['modelPorts'] = ast.literal_eval(lines[4].replace("\n", ""))
            update['currentTrainingLevel'] = ast.literal_eval(
                lines[5].replace("\n", ""))
            update['image_width'] = ast.literal_eval(
                lines[6].replace("\n", ""))
            update['image_height'] = ast.literal_eval(
                lines[7].replace("\n", ""))
            update['last_step'] = ast.literal_eval(lines[8].replace("\n", ""))
            update['loss'] = ast.literal_eval(lines[9].replace("\n", ""))
            update['perplexity'] = ast.literal_eval(
                lines[10].replace("\n", ""))
            update['checkpoint'] = ast.literal_eval(
                lines[11].replace("\n", ""))
            update['modelName'] = lines[12].replace("\n", "")
            update['modelPath'] = lines[13].replace("\n", "")
            update['modelOn'] = ast.literal_eval(lines[14].replace("\n", ""))
            return update
        except:
            pass
        update['notWorked'] = 0
        return update

    def get_process_update(self, captcha):
        file_location = self.WORK + captcha['username'].replace(
            " ", "") + "/" + captcha['title'].replace(" ", "") + "/" + str(captcha['modelNumber'])
        update = self.get_update(file_location)
        return update

    def update_captcha(self, captcha):
        file_location = self.WORK + captcha['username'].replace(
            " ", "") + "/" + captcha['title'].replace(" ", "") + "/" + str(captcha['modelNumber'])
        update = self.get_update(file_location)
        try:
            captcha['busyTraining'] = update['busyTraining']
            captcha['hasModel'] = update['hasModel']
            captcha['modelActive'] = update['modelActive']
        except:
            pass
        return captcha

    def update_all_captchas(self):
        for x in range(0, len(self.captchas)):
            self.captchas[x] = self.update_captcha(self.captchas[x])

    def get_results(self, captcha):
        file_location = self.WORK + captcha['username'].replace(" ", "") + "/" + captcha['title'].replace(
            " ", "") + "/" + str(captcha['modelNumber']) + "/test.txt"
        f = open(file_location)
        lines = f.readlines()
        count = 0
        correct = 0
        wrongs = []
        for line in lines:
            if (line.find("Step") != -1):
                temp = (line.replace('\n', '').split(',')[-1].split('%'))
                accuracy = temp[1]
                answer = temp[2]
                if float(accuracy) == 100.0:
                    correct += 1
                else:
                    wrongs.append(answer)
                count += 1

        final_results = {
            'correct': correct,
            'totalPredictions': count,
            'accuracy': str(correct / count * 100) + "%",
            'wrong_answers': str(wrongs)
        }
        return final_results


class GetResultsAPI(Resource):

    def validate_user(self, captcha):
        user = self.auth_source.get_username()
        if captcha['username'] == user:
            return True
        else:
            return False

    def __init__(self, **kwargs):
        self.data_source = kwargs['source']
        self.auth_source = kwargs['auth']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=bool, location='json')
        super(GetResultsAPI, self).__init__()

    def get(self, dataToken):
        if (not self.auth_source.get_and_verify()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)

        self.data_source.update_all_captchas()
        captcha = [
            captcha for captcha in self.data_source.captchas if captcha['dataToken'] == dataToken]
        if len(captcha) == 0:
            # return make_response(jsonify({'message': 'Unauthorized access'}), 403)
            abort(404)
        if not self.validate_user(captcha[0]):
            # return make_response(jsonify({'message': 'Unauthorized access'}), 403)
            abort(404)

        # Get the results
        results = self.data_source.get_results(captcha[0])
        return {'results': marshal(results, self.data_source.results_fields)}


class CaptchaListAPI(Resource):

    def __init__(self, **kwargs):
        self.data_source = kwargs['source']
        self.auth_source = kwargs['auth']
        self.reqparse = reqparse.RequestParser()
        super(CaptchaListAPI, self).__init__()

    def get(self):
        if (not self.auth_source.get_and_verify()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)
        # Build the captchas for the user
        user_captchas = []
        self.data_source.update_all_captchas()
        username = self.auth_source.get_username()

        for captcha in self.data_source.captchas:
            if captcha['username'] == username:
                user_captchas.append(captcha)
        return {'captchas': [marshal(captcha, self.data_source.captcha_fields) for captcha in user_captchas]}

    def build_filename(self, title, username):
        count = 1
        for captcha in self.data_source.captchas:
            if captcha['username'] == username:
                if captcha['title'] == title.replace(" ", ""):
                    count += 1

        # Count now keeps the current number for the file
        return count

    def post(self):
        if (not self.auth_source.get_and_verify()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)

        args = self.reqparse.parse_args()
        buf = request.files['captcha'].read()
        stuff = buf.decode('utf-8')
        posted_data = json.loads(stuff)
        posted_file = request.files['document'].read()
        count = self.build_filename(posted_data['title'], self.auth_source.get_username())  # auth.username())
        filename = self.data_source.FILE_DROP_LOCATION + self.auth_source.get_username().replace(" ", "") + "_" + posted_data['title'].replace(" ", "") + "_" + str(count) + ".zip"
        tempFile = open(filename, 'wb')
        tempFile.write(posted_file)
        tempFile.close()
        uid = str(uuid.uuid1())
        id_str = self.data_source.captchas[-1]['id'] + \
            1 if len(self.data_source.captchas) > 0 else 1
        captcha = {
            'id': id_str,
            'title': posted_data['title'],
            'username': self.auth_source.get_username(),  # auth.username(),
            'modelNumber': count,
            'dataToken': uid,
            'busyTraining': False,
            'hasModel': False,
            'modelActive': False
        }
        self.data_source.captchas.append(captcha)
        return {'captcha': marshal(captcha, self.data_source.captcha_fields)}, 201


class ExportAPI(Resource):

    def validate_user(self, captcha):
        user = self.auth_source.get_username()
        if captcha['username'] == user:
            return True
        else:
            return False

    def __init__(self, **kwargs):
        self.data_source = kwargs['source']
        self.auth_source = kwargs['auth']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        super(ExportAPI, self).__init__()

    def get(self, dataToken):
        if (not self.auth_source.get_and_verify()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)

        self.data_source.update_all_captchas()
        captcha = [
            captcha for captcha in self.data_source.captchas if captcha['dataToken'] == dataToken]
        if len(captcha) == 0:
            abort(404)
        if not self.validate_user(captcha[0]):
            abort(403)

        # Get the file to send
        file_location = self.data_source.MODELS + captcha[0]['username'].replace(
            " ", "") + "/" + captcha[0]['title'].replace(" ", "") + "/" + str(captcha[0]['modelNumber']) + "/exported-model"
        shutil.make_archive(file_location, 'zip', file_location)

        local_file_to_send = file_location + ".zip"
        if not os.path.isabs(local_file_to_send):
            self.data_source.logger.warning("The path is not an abs path")
            if (local_file_to_send[0] == '.'):
                local_file_to_send = local_file_to_send[1:]


            local_file_to_send = os.getcwd() + local_file_to_send

        return send_file(local_file_to_send, attachment_filename='exported_model.zip')


class GetProgressAPI(Resource):

    def validate_user(self, captcha):
        user = self.auth_source.get_username()
        if captcha['username'] == user:
            return True
        else:
            return False

    def __init__(self, **kwargs):
        self.data_source = kwargs['source']
        self.auth_source = kwargs['auth']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=bool, location='json')
        super(GetProgressAPI, self).__init__()

    def get(self, dataToken):
        if (not self.auth_source.get_and_verify()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)

        self.data_source.update_all_captchas()
        captcha = [
            captcha for captcha in self.data_source.captchas if captcha['dataToken'] == dataToken]
        if len(captcha) == 0:
            abort(404)
        if not self.validate_user(captcha[0]):
            abort(403)

        # Get the update
        update = self.data_source.get_process_update(captcha[0])

        training_progress = {
            'id': captcha[0]['id'],
            'title': captcha[0]['title'],
            'username': captcha[0]['username'],
            'modelNumber': captcha[0]['modelNumber'],
            'dataToken': captcha[0]['dataToken'],
            'busyTraining': captcha[0]['busyTraining'],
            'hasModel': captcha[0]['hasModel'],
            'modelActive': captcha[0]['modelActive'],
            'currentTrainingLevel': update['currentTrainingLevel'],
            'last_step': update['last_step'],
            'loss': update['loss'],
            'perplexity': update['perplexity'],
            'checkpoint': update['checkpoint']
        }
        return {'update': marshal(training_progress, self.data_source.training_progress_fields)}


class ToggleModelAPI(Resource):

    def validate_user(self, captcha):
        user = self.auth_source.get_username()
        if captcha['username'] == user:
            return True
        else:
            return False

    def __init__(self, **kwargs):
        self.data_source = kwargs['source']
        self.auth_source = kwargs['auth']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('dataToken', type=str, location='json')
        self.reqparse.add_argument('active', type=bool, location='json')
        super(ToggleModelAPI, self).__init__()

    def post(self):
        if (not self.auth_source.get_and_verify()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)

        args = self.reqparse.parse_args()

        captcha = [
            captcha for captcha in self.data_source.captchas if captcha['dataToken'] == args['dataToken']]
        if len(captcha) == 0:
            abort(404)
        if not self.validate_user(captcha[0]):
            abort(403)

        # We should now find and modify the file
        self.data_source.change_model_status(captcha[0], args['active'])
        return {'captcha': marshal(captcha[0], self.data_source.captcha_fields)}


class SolveCaptchaAPI(Resource):

    def validate_user(self, captcha):
        user = self.auth_source.get_username()
        if captcha['username'] == user:
            return True
        else:
            return False

    def __init__(self, **kwargs):
        self.data_source = kwargs['source']
        self.auth_source = kwargs['auth']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('dataToken', type=str, location='json')
        self.reqparse.add_argument('image', type=str, location='json')
        super(SolveCaptchaAPI, self).__init__()

    def post(self):
        if (not self.auth_source.get_and_verify()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)

        args = self.reqparse.parse_args()

        captcha = [
            captcha for captcha in self.data_source.captchas if captcha['dataToken'] == args['dataToken']]
        if len(captcha) == 0:
            abort(404)
        if not self.validate_user(captcha[0]):
            abort(403)

        # We should send their request to the captcha solving server
        answer = self.data_source.get_captcha_solution(
            captcha[0], str(args['image']))

        return {'solution': marshal(answer, self.data_source.solution_fields)}


class CaptchaAPI(Resource):

    def validate_user(self, captcha):
        user = self.auth_source.get_username()
        if captcha['username'] == user:
            return True
        else:
            return False

    def __init__(self, **kwargs):
        self.data_source = kwargs['source']
        self.auth_source = kwargs['auth']
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        super(CaptchaAPI, self).__init__()

    def get(self, id):
        if (not self.auth_source.get_and_verify()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)

        self.data_source.update_all_captchas()
        captcha = [
            captcha for captcha in self.data_source.captchas if captcha['id'] == id]
        if len(captcha) == 0:
            abort(404)
        if not self.validate_user(captcha[0]):
            abort(403)
        return {'captcha': marshal(captcha[0], self.data_source.captcha_fields)}

    def put(self, id):
        if (not self.auth_source.get_and_verify()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)
        captcha = [
            captcha for captcha in self.data_source.captchas if captcha['id'] == id]
        if len(captcha) == 0:
            abort(404)
        if not self.validate_user(captcha[0]):
            abort(403)
        captcha = captcha[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                captcha[k] = v
        return {'captcha': marshal(captcha, self.data_source.captcha_fields)}

    def delete(self, id):
        if (not self.auth_source.get_and_verify()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)
        captcha = [
            captcha for captcha in self.data_source.captcas if captcha['id'] == id]
        if len(captcha) == 0:
            abort(404)
        if not self.validate_user(captcha[0]):
            abort(403)
        self.data_source.captchas.remove(captcha[0])
        return {'result': True}


class UserAPI(Resource):
    def __init__(self, **kwargs):
        self.data_source = kwargs['source']
        self.auth_source = kwargs['auth']

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, location='json')
        self.reqparse.add_argument('password', type=str, location='json')

        super(UserAPI, self).__init__()

    def get(self):
        username = request.args.get('username')
        password = request.args.get('password')
        #Here we can get the username and password for registration
        if (self.data_source.registerUser(username, password)):
            return {'result' : True}
        else:
            return {'result' : False}

    def post(self):
        args = self.reqparse.parse_args()
        username = args['username']
        password = args['password']

        #Here we can get the username and password for registration
        if (self.data_source.registerUser(username, password)):
            return {'result' : True}
        else:
            return {'result' : False}






class GenerateTokenAPI(Resource):

    def validate_user(self, captcha):
        user = self.auth_source.get_username()
        if captcha['username'] == user:
            return True
        else:
            return False

    def __init__(self, **kwargs):
        self.data_source = kwargs['source']
        self.auth_source = kwargs['auth']

        self.reqparse = reqparse.RequestParser()
        super(GenerateTokenAPI, self).__init__()

    def get(self):
        if (not self.auth_source.verify_connect()):
            return make_response(jsonify({'message': 'Unauthorized access'}), 403)

        # First check how many tokens the user has
        username = request.authorization["username"]
        for user in self.data_source.users:
            if username == user.username:
                count = len(user.tokens)
                if count >= self.data_source.max_tokens:
                    return make_response(jsonify({'token': '', 'message': 'maximum amount of tokens generated'}), 200)
                lst = [random.choice(string.ascii_letters + string.digits)
                       for n in range(128)]
                str_ = "".join(lst)
                user.tokens[uuid.uuid1()] = [str_, time.time()]
                return make_response(jsonify({'message': 'success', 'token': str_}), 200)
        # We should now find and modify the file

        return make_response(jsonify({'token': '', 'message': 'token gen failed'}), 200)


class ApiServer:
    def __init__(self, host="0.0.0.0", port="5000", is_debug=False, file_drop="./Unsorted/", max_tokens=5, server_location="./", user_file="users.txt", work_folder="./Busy", model_folder="./Model", logger=logging.getLogger("Captcha22 Server API")):
        self.logger = logger
        self.logger.info("Captcha22 Server API Start")

        # Create the app
        self.app = Flask(__name__, static_url_path="")

        self.cors = CORS(self.app)

        self.api = Api(self.app)

        self.host = host
        self.port = port
        self.debug = is_debug

        self.source = data_source(file_drop, max_tokens, server_location, user_file, work_folder, model_folder, self.logger)

        self.systemAuth = AuthSystem(self.source)

        self.api.add_resource(CaptchaListAPI, '/captcha22/api/v1.0/captchas', endpoint='captchas',
                              resource_class_kwargs={'source': self.source, 'auth': self.systemAuth})
        self.api.add_resource(CaptchaAPI, '/captcha22/api/v1.0/captchas/<int:id>', endpoint='captcha',
                              resource_class_kwargs={'source': self.source, 'auth': self.systemAuth})
        self.api.add_resource(ExportAPI, '/captcha22/api/v1.0/export_model/<string:dataToken>',
                              endpoint='export_model', resource_class_kwargs={'source': self.source, 'auth': self.systemAuth})
        self.api.add_resource(GetProgressAPI, '/captcha22/api/v1.0/training_update/<string:dataToken>',
                              endpoint='training_update', resource_class_kwargs={'source': self.source, 'auth': self.systemAuth})
        self.api.add_resource(GetResultsAPI, '/captcha22/api/v1.0/results/<string:dataToken>',
                              endpoint='results', resource_class_kwargs={'source': self.source, 'auth': self.systemAuth})
        self.api.add_resource(ToggleModelAPI, '/captcha22/api/v1.0/activate_model', endpoint='activate_model',
                              resource_class_kwargs={'source': self.source, 'auth': self.systemAuth})
        self.api.add_resource(SolveCaptchaAPI, '/captcha22/api/v1.0/solve_captcha', endpoint='solve_captcha',
                              resource_class_kwargs={'source': self.source, 'auth': self.systemAuth})
        self.api.add_resource(GenerateTokenAPI, '/captcha22/api/v1.0/generate_token', endpoint='generate_token',
                              resource_class_kwargs={'source': self.source, 'auth': self.systemAuth})
        self.api.add_resource(UserAPI, '/captcha22/api/v1.0/user', endpoint='user',
                              resource_class_kwargs={'source': self.source, 'auth': self.systemAuth})

    def main(self):
        self.app.run(host=self.host, port=self.port, debug=self.debug)


# For production servers, remember to remove the debug flag
if __name__ == '__main__':

    server = ApiServer()
    server.main()
