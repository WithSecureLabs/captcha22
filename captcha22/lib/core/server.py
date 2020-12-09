#!/usr/bin/python3
import sys
import argparse
import logging
from threading import Thread

# Import libs

# API classes
#from lib.api.captcha22_server_api import *

#from lib.crackers.pyppeteer_cracking import *
# Server classes
#from lib.server.captcha22 import Captcha22


#### SERVER ####
def server(args):
    from lib.server.captcha22 import Captcha22
    logger = logging.getLogger("Captcha22 Engine")
    server = Captcha22(args.max_steps, args.loss_threshold, args.perplexity_threshold, args.split_percentage,
                       args.starting_port, args.input_folder, args.work_folder, args.model_folder, logger)
    server.main()

#### API ####
def server_api(args):
    from lib.api.server import ApiServer
    logger = logging.getLogger("Captcha22 Server API")
    server = ApiServer(args.host, args.port, args.enable_debugging, args.file_drop, args.max_tokens, args.server_location,
                       args.user_file, args.work_folder, args.model_folder, logger)
    server.main()

#### UI ####
def server_ui(args):
    from lib.api.ui import UIServer
    logger = logging.getLogger("Captcha22 Server UI")
    server = UIServer(args.api_ip, args.api_port, args.api_endpoint, args.ui_port, args.docker_server, args.container_name, args.image_name, logger)

    server.main()

### FULL ####
def server_full(args):
    from lib.server.captcha22 import Captcha22
    from lib.api.server import ApiServer
    from lib.api.ui import UIServer
    engine_logger = logging.getLogger("Captcha22 Engine")
    api_logger = logging.getLogger("Captcha22 Server API")
    ui_logger = logging.getLogger("Captcha22 Server UI")

    engine_server = Captcha22(args.max_steps, args.loss_threshold, args.perplexity_threshold, args.split_percentage,
                        args.starting_port, args.input_folder, args.work_folder, args.model_folder, engine_logger)
    api_server = ApiServer(args.host, args.port, args.enable_debugging, args.input_folder, args.max_tokens, args.server_location,
                        args.user_file, args.work_folder, args.model_folder, api_logger)
    ui_server = UIServer(args.api_ip, args.port, args.api_endpoint, args.ui_port, args.docker_server, args.container_name, args.image_name, ui_logger)

    def thread_system(arg):
        arg.main()

    thread_engine = Thread(target = thread_system, args = (engine_server, ))
    thread_api = Thread(target = thread_system, args = (api_server, ))
    thread_engine.start()
    thread_api.start()

    ui_server.main()




if __name__ == "__main__":
    print ("Please use captcha22 from terminal")

