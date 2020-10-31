#!/usr/bin/python3
import sys
import argparse
import logging

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


if __name__ == "__main__":
    print ("Please use captcha22 from terminal")

