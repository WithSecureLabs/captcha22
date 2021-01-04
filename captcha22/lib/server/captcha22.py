#!/usr/bin/python3
import numpy
import os
import time
import glob
import cv2
import ast
import argparse
import logging


class captcha:
    def __init__(self, path, logger):
        self.path = path

        self.logger = logger

        self.hasTrained = False
        self.busyTraining = False
        self.hasModel = False
        self.modelActive = False
        self.modelPorts = -1
        self.currentTrainingLevel = -1
        self.image_width = 0
        self.image_heigth = 0
        self.last_step = 0
        self.loss = 0
        self.perplexity = 0
        self.checkpoint = 0
        self.modelName = "null"
        self.modelPath = "null"
        self.modelOn = False

        try:
            f = open(self.path + 'model.txt')
            lines = f.readlines()
            self.hasTrained = ast.literal_eval(lines[0].replace("\n", ""))
            self.busyTraining = ast.literal_eval(lines[1].replace("\n", ""))
            self.hasModel = ast.literal_eval(lines[2].replace("\n", ""))
            self.modelActive = ast.literal_eval(lines[3].replace("\n", ""))
            self.modelPorts = ast.literal_eval(lines[4].replace("\n", ""))
            self.currentTrainingLevel = ast.literal_eval(
                lines[5].replace("\n", ""))
            self.image_width = ast.literal_eval(lines[6].replace("\n", ""))
            self.image_height = ast.literal_eval(lines[7].replace("\n", ""))
            self.last_step = ast.literal_eval(lines[8].replace("\n", ""))
            self.loss = ast.literal_eval(lines[9].replace("\n", ""))
            self.perplexity = ast.literal_eval(lines[10].replace("\n", ""))
            self.checkpoint = ast.literal_eval(lines[11].replace("\n", ""))
            self.modelName = lines[12].replace("\n", "")
            self.modelPath = lines[13].replace("\n", "")
            self.modelOn = ast.literal_eval(lines[14].replace("\n", ""))

        except:
            self.get_image_size()
            self.update_file()
            pass

    def get_image_size(self):
        images = glob.glob(self.path + "data/*.png")
        img = cv2.imread(images[0])
        self.image_width = img.shape[1]
        self.image_height = img.shape[0]

    def update_from_file(self):
        f = open(self.path + 'model.txt')
        lines = f.readlines()
        self.hasTrained = ast.literal_eval(lines[0].replace("\n", ""))
        self.busyTraining = ast.literal_eval(lines[1].replace("\n", ""))
        self.hasModel = ast.literal_eval(lines[2].replace("\n", ""))
        self.modelActive = ast.literal_eval(lines[3].replace("\n", ""))
        self.modelPorts = ast.literal_eval(lines[4].replace("\n", ""))
        self.currentTrainingLevel = ast.literal_eval(
            lines[5].replace("\n", ""))
        self.image_width = ast.literal_eval(lines[6].replace("\n", ""))
        self.image_height = ast.literal_eval(lines[7].replace("\n", ""))
        self.last_step = ast.literal_eval(lines[8].replace("\n", ""))
        self.loss = ast.literal_eval(lines[9].replace("\n", ""))
        self.perplexity = ast.literal_eval(lines[10].replace("\n", ""))
        self.checkpoint = ast.literal_eval(lines[11].replace("\n", ""))
        self.modelName = lines[12].replace("\n", "")
        self.modelPath = lines[13].replace("\n", "")
        self.modelOn = ast.literal_eval(lines[14].replace("\n", ""))

    def update_file(self):
        f = open(self.path + 'model.txt', 'w')
        f.write(str(self.hasTrained) + "\n")
        f.write(str(self.busyTraining) + "\n")
        f.write(str(self.hasModel) + "\n")
        f.write(str(self.modelActive) + "\n")
        f.write(str(self.modelPorts) + "\n")
        f.write(str(self.currentTrainingLevel) + "\n")
        f.write(str(self.image_width) + "\n")
        f.write(str(self.image_height) + "\n")
        f.write(str(self.last_step) + "\n")
        f.write(str(self.loss) + "\n")
        f.write(str(self.perplexity) + "\n")
        f.write(str(self.checkpoint) + "\n")
        f.write(str(self.modelName) + "\n")
        f.write(str(self.modelPath) + "\n")
        f.write(str(self.modelOn) + "\n")

    def export_model(self):
        self.logger.info("Going to extract the model")
        os.system("(cd " + self.path + " && aocr export --max-height " + str(
            self.image_height) + " --max-width " + str(self.image_width) + " exported-model)")
        time.sleep(5)

    def run_model(self):
        self.logger.info("Starting serving model")
        self.logger.info("nohup tensorflow_model_server --port=" + str(self.modelPorts) + " --rest_api_port=" + str(self.modelPorts + 1) +
              " --model_name=" + self.modelName + " --model_base_path=" + os.getcwd() + "/" + self.modelPath + " 2&> /dev/null &")
        os.system("nohup tensorflow_model_server --port=" + str(self.modelPorts) + " --rest_api_port=" + str(self.modelPorts + 1) +
                  " --model_name=" + self.modelName + " --model_base_path=" + os.getcwd() + "/" + self.modelPath + " 2&> /dev/null &")

    def stop_model(self):
        self.logger.info("Stopping serving model")
        os.system("kill $(ps aux | grep 'tensorflow_model_server --port=" +
                  str(self.modelPorts) + "' | awk '{print $2}')")

    def model_trained(self):
        return self.hasTrained

    def busy_training(self):
        return self.busyTraining

    def test_training_level(self):
        self.logger.info("Testing training level")
        # Go read the aocr log
        f = open(self.path + "aocr.log")
        lines = f.readlines()
        lastUpdate = ""
        for line in lines:
            if line.find("Step") != -1:
                lastUpdate = line

        values = lastUpdate.split(',')
        step = ast.literal_eval(values[1].split('Step ')[1].split(':')[0])

        # We need to combine two values, the current step and the last saved step. This gives us the total step.
        current_checkpoint = 0
        try:
            f = open(self.path + "/checkpoints/checkpoint")
            lines = f.readlines()
            current_checkpoint = ast.literal_eval(
                lines[0].split('ckpt-')[1].split("\"")[0])
        except:
            self.logger.info("No current checkpoint")
            pass

        while (step > 100):
            step -= 100

        self.last_step = current_checkpoint + step
        self.loss = ast.literal_eval(values[2].split('loss: ')[1])
        self.perplexity = ast.literal_eval(values[3].split('perplexity: ')[1].split(
            '.')[0] + "." + values[3].split('perplexity: ')[1].split('.')[1])
        self.checkpoint = current_checkpoint

        self.logger.info("Values are: ")
        self.logger.info("Step: {}".format(self.last_step))
        self.logger.info("Loss: {}".format(self.loss))
        self.logger.info("Perplexity: {}".format(self.perplexity))
        self.logger.info("Checkpoint: {}".format(self.checkpoint))

        self.update_file()

    def determine_endpoint(self, steps, loss, perplex):
        if self.checkpoint >= steps:
            # Time to end
            return True

        if self.loss < loss and self.perplexity < perplex:
            return True

        return False

    def stop_training(self):
        # Sometime the kill is not respected. Do this three times to ensure it is killed
        self.logger.info("Going to stop training")
        os.system("kill $(ps aux | grep 'aocr' | awk '{print $2}')")
        self.logger.info("training stopped, waiting")
        time.sleep(5)
        os.system("kill $(ps aux | grep 'aocr' | awk '{print $2}')")
        self.logger.info("training stopped, waiting")
        time.sleep(5)
        os.system("kill $(ps aux | grep 'aocr' | awk '{print $2}')")
        self.logger.info("training stopped, waiting")
        time.sleep(5)
        self.busyTraining = False
        self.hasTrained = True
        self.update_file()

    def test_training(self):
        self.logger.info("Testing")
        self.logger.info("(cd " + self.path + " && aocr test --max-height " + str(self.image_height) +
              " --max-width " + str(self.image_width) + " labels/testing.tfrecords 2>&1 | tee test.txt)")
        os.system("(cd " + self.path + " && aocr test --max-height " + str(self.image_height) +
                  " --max-width " + str(self.image_width) + " labels/testing.tfrecords 2>&1 | tee test.txt)")
        time.sleep(30)

    def start_training(self):
        self.logger.info("Starting training")
        self.busyTraining = True
        self.update_file()
        os.system("(cd " + self.path + " && nohup aocr train --max-height " + str(self.image_height) +
                  " --max-width " + str(self.image_width) + " labels/training.tfrecords &>/dev/null &)")


class Captcha22:
    def __init__(self, max_steps=2000, loss_threshold=0.0002, perplexity_threshold=1.00018, split_percentage=90.0, starting_port=9000, input_folder="./Unsorted", work_folder="./Busy",  model_folder="./Model", logger=logging.getLogger("Captcha22 Engine")):

        self.logger = logger

        self.logger.info("Captcha22 engine start")
        self.busyTraining = False

        self.training_steps_max = int(max_steps)
        self.training_loss_min = float(loss_threshold)
        self.training_perplexity_min = float(perplexity_threshold)

        self.currentPort = int(starting_port)

        self.unsorted_URL = input_folder
        self.busy_URL = work_folder
        self.model_URL = model_folder

        try:
             os.mkdir(self.unsorted_URL)
        except FileExistsError:
            pass

        try:
             os.mkdir(self.busy_URL)
        except FileExistsError:
            pass

        try:
             os.mkdir(self.model_URL)
        except FileExistsError:
            pass




        self.data_split = float(split_percentage)

        self.new_models = []
        self.existing_models = []



    def copy_files(self, file):

        self.logger.info("Starting the copy of files")
        names = file.split(".")[0].split("/")[-1].split("_")
        if (file[0] == "."):
            names = file.split(".")[1].split("/")[-1].split("_")


        # Creating folder structure data
        os.system('mkdir ' + self.busy_URL + "/" + names[0])
        os.system('mkdir ' + self.busy_URL + "/" + names[0] + "/" + names[1])
        os.system('mkdir ' + self.busy_URL + "/" +
                  names[0] + "/" + names[1] + "/" + names[2])
        os.system('mkdir ' + self.busy_URL + "/" +
                  names[0] + "/" + names[1] + "/" + names[2] + "/" + "labels")

        # Creating folder structure for model
        os.system('mkdir ' + self.model_URL + "/" + names[0])
        os.system('mkdir ' + self.model_URL + "/" + names[0] + "/" + names[1])
        os.system('mkdir ' + self.model_URL + "/" +
                  names[0] + "/" + names[1] + "/" + names[2])
        os.system('mkdir ' + self.model_URL + "/" +
                  names[0] + "/" + names[1] + "/" + names[2] + "/exported-model")
        os.system('mkdir ' + self.model_URL + "/" +
                  names[0] + "/" + names[1] + "/" + names[2] + "/exported-model/1")

        # Copy the file to the directory
        os.system("cp " + file.replace("\n", "") + " " + self.busy_URL +
                  "/" + names[0] + "/" + names[1] + "/" + names[2])
        os.system("rm " + file.replace("\n", ""))

        # Unzip the file
        os.system("unzip " + self.busy_URL + "/" + names[0] + "/" + names[1] + "/" + names[2] + "/" + file.split(
            "/")[-1] + " -d " + self.busy_URL + "/" + names[0] + "/" + names[1] + "/" + names[2] + "/")
        os.system("rm " + self.busy_URL + "/" +
                  names[0] + "/" + names[1] + "/" + names[2] + "/" + file.split("/")[-1])

    def export_model(self, model):
        paths = model.path.split("/")
        shortPath = paths[-4] + "/" + paths[-3] + "/" + paths[-2]
        # Ask model to create the model
        model.export_model()
        # Copy the model to the correct path for safekeeping
        os.system("cp -r " + model.path + "exported-model/* " + self.model_URL + "/" + shortPath + "/exported-model/1/")
        self.logger.info("Model copied")

    def run_model(self, model):
        # Single command to start the model
        self.logger.info("Start model")
        model.run_model()

    def stop_model(self, model):
        self.logger.info("Stop model")
        model.stop_model()

    def label_captchas(self, file):
        # Function used to label the captchas
        names = file.split(".")[0].split("/")[-1].split("_")
        if (file[0] == '.'):
            names = file.split(".")[1].split("/")[-1].split("_")
        read_dir = self.busy_URL + "/" + \
            names[0] + "/" + names[1] + "/" + names[2] + "/data/"
        write_dir = self.busy_URL + "/" + \
            names[0] + "/" + names[1] + "/" + names[2] + "/labels/"

        self.logger.info("Directories is:")
        self.logger.info(read_dir)
        self.logger.info(write_dir)

        onlyfiles = glob.glob(read_dir + "*.png")

        count = len(onlyfiles)
        train_count = int(count * (self.data_split / 100.0))
        test_count = count - train_count

        # Create train labels
        count = 0
        labels = open(write_dir + "training_labels.txt", "w")
        while (count < train_count):
            file = onlyfiles[count]
            answer = file.replace('.png', '').split('/')[-1].split('_')[-1]

            labels.write(self.busy_URL + "/" + names[0] + "/" + names[1] + "/" +
                         names[2] + "/data/" + file.split('/')[-1] + ' ' + answer + '\n')

            count += 1

        labels.close()

        # Create test labels
        count = 0
        labels = open(write_dir + "testing_labels.txt", "w")
        while (count < test_count):
            file = onlyfiles[train_count + count]

            answer = file.replace('.png', '').split('/')[-1].split('_')[-1]
            labels.write(self.busy_URL + "/" + names[0] + "/" + names[1] + "/" +
                         names[2] + "/data/" + file.split('/')[-1] + ' ' + answer + '\n')

            count += 1
        labels.close()

    def generate_aocr_records(self, file):
        names = file.split(".")[0].split("/")[-1].split("_")
        if (file[0] == '.'):
            names = file.split(".")[1].split("/")[-1].split("_")

        # Creating folder structure data
        os.system('aocr dataset ' + self.busy_URL + "/" + names[0] + "/" + names[1] + "/" + names[2] + "/labels/training_labels.txt " +
                  self.busy_URL + "/" + names[0] + "/" + names[1] + "/" + names[2] + "/labels/training.tfrecords")
        time.sleep(1)
        os.system('aocr dataset ' + self.busy_URL + "/" + names[0] + "/" + names[1] + "/" + names[2] + "/labels/testing_labels.txt " +
                  self.busy_URL + "/" + names[0] + "/" + names[1] + "/" + names[2] + "/labels/testing.tfrecords")
        time.sleep(5)

    def create_model(self, file):
        self.logger.info(file)
        names = file.split(".")[0].split("/")[-1].split("_")
        if (file[0] == '.'):
            names = file.split(".")[1].split("/")[-1].split("_")
        path = self.busy_URL + "/" + names[0] + \
            "/" + names[1] + "/" + names[2] + "/"
        model = captcha(path, self.logger)

        if model.model_trained():
            self.existing_models.append(model)
        else:
            self.new_models.append(model)

    def reload_models(self, path):
        model = captcha(path, self.logger)
        if model.model_trained():
            self.existing_models.append(model)
        else:
            if model.busy_training():
                model.start_training()

            self.new_models.append(model)

    def check_files(self):
        self.logger.info("Checking if there are any new files")

        files = glob.glob(self.unsorted_URL + "/*.zip")

        self.logger.info(files)

        self.logger.info("Start running")

        for file in files:
            self.logger.info("Copy files")
            self.copy_files(file)
            self.logger.info("Create labels")
            self.label_captchas(file)
            self.logger.info("Generate aocr")
            self.generate_aocr_records(file)
            self.logger.info("Create model")
            self.create_model(file)
            self.logger.info("Updating file")
            self.update_file()
            self.logger.info("Done")

    def update_file(self):
        f = open('models.txt', 'w')
        for model in self.existing_models:
            f.write(model.path + "\n")

        for model in self.new_models:
            f.write(model.path + "\n")

        f.close()

    def continue_training(self):
        if len(self.new_models) == 0:
            self.busyTraining = False
            return

        # If there is models, we need to check the first one.
        self.busyTraining = True
        model = self.new_models[0]

        # Check if this model is busy training
        if model.busy_training():
            # Request an update and kill if needed
            self.logger.info("Model update")
            model.test_training_level()
            if model.determine_endpoint(self.training_steps_max, self.training_loss_min, self.training_perplexity_min):
                # We need to stop training
                model.stop_training()
                # Do other things such as moving the model

                # Test the training of the model
                model.test_training()

                # Export the model
                self.export_model(model)
                model.hasModel = True

                paths = model.path.split("/")
                shortPath = paths[1] + "/" + paths[2] + "/" + paths[3]
                model.modelName = paths[1] + "_" + paths[2]
                model.modelPath = self.model_URL + "/" + shortPath + "/exported-model/"
                model.modelPorts = self.currentPort
                self.currentPort + 2
                model.update_file()

                # Create the server for the model
                # Run the server

                self.existing_models.append(model)
                # Delete model
                del self.new_models[0]
                self.update_file()

        else:
            self.logger.info("Going to start the model training procedure")
            # Model not training, start training
            model.start_training()

    def start_model_server(self):
        self.logger.info("Checking the models")
        self.logger.info(len(self.existing_models))
        for model in self.existing_models:
            model.update_from_file()
            # Check if the start var has been set and active not, then start
            if model.modelOn and not model.modelActive:
                # The model needs to be started
                self.logger.info("Starting model")
                model.modelActive = True
                self.run_model(model)

            if not model.modelOn and model.modelActive:
                # The model is on but needs to be killed
                self.logger.info("Killing model")
                model.modelActive = False
                self.stop_model(model)
            model.update_file()

    def run_server(self):

        while (True):
            if (not self.busyTraining):
                self.check_files()
            self.continue_training()
            if (not self.busyTraining):
                self.start_model_server()
            self.logger.info("Starting wait cycle")
            time.sleep(30)

    def first_start(self):
        # Load all models
        #New loading method
        first_layer = glob.glob(self.busy_URL + "/*")
        all_layers = []
        for user in first_layer:
            second_layer = glob.glob(user + "/*")
            for client in second_layer:
                third_layer = glob.glob(client + "/*")
                for layer in third_layer:
                    all_layers.append(layer)

        for layer in all_layers:
            self.reload_models(layer + "/")
        self.update_file()

    def main(self):
        self.first_start()
        self.run_server()


if __name__ == "__main__":
    server = Captcha22()
    server.main()
