#!/usr/bin/python3

import argparse
import os
import docker
import logging
from io import BytesIO
import signal
import sys

#Currently this will only build, create, and start the docker
#image for us. We also only have control over the name of the
#docker image and API endpoit, later versions will control more.

class UIServer:
    def __init__(self, api_ip="172.17.0.1", api_port=5000, api_endpoint="/captcha22/api/v1.0/", ui_port=8080, docker_server="unix://var/run/docker.sock", container_name="captcha22/captcha22_ui", image_name="tinusgreen/captcha22_ui:latest", logger=logging.getLogger("Captcha22 Server UI")):
        self.logger = logger
        self.logger.info("Captcha22 Server UI Start")

        self.image_name = image_name
        self.api_ip = api_ip
        self.api_port = api_port
        self.api_endpoint = api_endpoint
        self.docker_server = docker_server

        self.ui_port = ui_port
        self.container_name = container_name

        self.endpoint = "\'\"http://" + self.api_ip + ":" + str(self.api_port) + self.api_endpoint + "\"\'"

        self.build_client = docker.APIClient(base_url=self.docker_server)
        self.run_client = docker.from_env()

        self.dockerfile = '''
        FROM ''' + self.image_name + '''
        ENV API_URL ''' +  self.endpoint + '''
        RUN npm run build
        EXPOSE 8080
        CMD [ "http-server", "dist" ]
        '''

    def buildImage(self):
        self.logger.info("Building UI docker image")
        f = BytesIO(self.dockerfile.encode('utf-8'))
        response = [line for line in self.build_client.build(fileobj=f, rm=True, tag=self.container_name)]

        for line in response:
            self.logger.info(line)


    def runImage(self):
        self.logger.info("Starting UI Docker Container")
        self.container = self.run_client.containers.run(self.container_name, ports={'8080/tcp' : ('0.0.0.0', self.ui_port)}, detach=True)
        self.logger.info("UI running, press Ctrl+C to stop")

    def killImage(self):
        self.container.kill()

    def signal_handler(self, sig, frame):
        self.logger.info("SIGINT received, stopping UI Docker Container")
        self.killImage()
        self.logger.info("UI stopped, goodbye")

    def main(self):
        self.buildImage()
        self.runImage()
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.pause()


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    server = UIServer()
    server.main()
