#!/usr/bin/python3

import argparse
import site
import sys
import logging

try:
    sites = site.getsitepackages()

    for site_path in sites:
        sys.path.append(site_path + "/captcha22")
except:
    pass

logging.basicConfig(level=logging.INFO)

import captcha22 as _;

for path in _.__path__:
    sys.path.append(path)

from lib.core.client import (api_basic, api_full, captcha_labeller,
                                captcha_typer, client_api, cracker,
                                cracker_baseline, cracker_pyppeteer,
                                label, label_generator)
from lib.core.server import server, server_api

def client_help(args):
    sys.exit(1)

def server_help(args):
    sys.exit(1)



def main():

    main_parser = argparse.ArgumentParser(
        prog="captcha22", description=(
            "CAPTCHA22 is a program that can be used to build models of CAPTCHAs and automate the cracking process."))

    subparsers = main_parser.add_subparsers(title="Component")

    ### First level ###
    client_parser = subparsers.add_parser(
        "client", help="Use to execute the CAPTCHA22 Client")
    server_parser = subparsers.add_parser(
        "server", help="Use to execute the CAPTCHA22 Server")

    client_parser.set_defaults(func=client_help)
    server_parser.set_defaults(func=server_help)

    client_subparsers = client_parser.add_subparsers(title="Commands")
    server_subparsers = server_parser.add_subparsers(title="Commands")

    #### HELPERS ####
    label_parser = client_subparsers.add_parser(
        "label", help="Use to execute CAPTCHA labelling helper scripts")
    label_parser.set_defaults(func=label)

    label_group = label_parser.add_argument_group()

    label_group.add_argument("--script", default="captchaTyper",
                             help="Type of script to execute.",
                             choices=["captchaTyper",
                                      "captchaLabeller",
                                      "labelGenerator"]
                             )
    label_group.add_argument("--input", default="./input/",
                             help="Input folder for CAPTCHAs. Default is './input/'")
    label_group.add_argument("--output", default="./data/",
                             help="Output folder for CAPTCHAs. Default is './data/'")
    label_group.add_argument("--image-type", default="png",
                             help="File type of the CAPTCHA images. Default is 'png'")

    #### APIs ####
    api_parser = client_subparsers.add_parser(
        "api", help="Use to execute the CAPTCHA API scripts")
    api_parser.set_defaults(func=client_api)

    api_group = api_parser.add_argument_group()

    api_group.add_argument("--script", default="full",
                           help="Type of script to execute. Choose out between full or basic, default is full")
    api_group.add_argument("--server-url", default="http://127.0.0.1",
                           help="Specify the URL of the CAPTCHA22 API Server, default is http://127.0.0.1")
    api_group.add_argument("--server-path", default="/captcha22/api/v1.0/",
                           help="Specify the API Endpoint Path of the CAPTCHA22 API Server, default is /captcha22/api/v1.0/")
    api_group.add_argument("--server-port", default="5000",
                           help="Specify the PORT of the CAPTCHA22 API Server, default is 5000")
    api_group.add_argument("--username", default=None,
                           help="Username used for connection to CAPTCHA22")
    api_group.add_argument("--password", default=None,
                           help="Password used for connection to CAPTCHA22")
    api_group.add_argument("--input", default="./input/",
                           help="Specify the input directory, default is input/")
    api_group.add_argument("--image-type", default="png",
                           help="Specify the image file type, default is png")
    api_group.add_argument("--captcha-id", default=None,
                           help="Specify the captch-id to use")

    #### CRACKERS ####

    cracker_parser = client_subparsers.add_parser(
        "cracker", help="Select from available CAPTCHA cracking scripts")
    cracker_parser.set_defaults(func=cracker)

    cracker_group = cracker_parser.add_argument_group()

    cracker_group.add_argument(
        "--script", default=None, help="Type of script to execute.", choices=["baseline", "pyppeteer"])
    cracker_group_server = cracker_parser.add_argument_group(
        title="CAPTCHA22 Server Arguments")

    # Arguments
    # Server
    cracker_group_server.add_argument("--server-url", default="http://127.0.0.1",
                                      help="Specify the URL of the CAPTCHA22 API Server, default is http://127.0.0.1")
    cracker_group_server.add_argument("--server-path", default="/captcha22/api/v1.0/",
                                      help="Specify the API Endpoint Path of the CAPTCHA22 API Server, default is /captcha22/api/v1.0/")
    cracker_group_server.add_argument(
        "--server-port", default=5000, type=int, help="Specify the PORT of the CAPTCHA22 API Server, default is 5000")

    # Credentials
    cracker_group_server.add_argument(
        "--username", default=None, help="Username used for connection to CAPTCHA22, default will be prompted")
    cracker_group_server.add_argument(
        "--password", default=None, help="Password used for connection to CAPTCHA22, default will be prompted")

    # Session var
    cracker_group_server.add_argument(
        "--max-session-duration", default=1800, type=int, help="Specify the time that a JWT session remains active")

    cracker_group_options = cracker_parser.add_argument_group(
        title="Local CAPTCHA Processing Arguments")

    # Options var
    cracker_group_options.add_argument(
        "--use-hashes", default=False, help="Use hash comparisons to aid cracking process", action="store_true")
    cracker_group_options.add_argument(
        "--use-filter", default=False, help="Use image filter to aid cracking process", action="store_true")
    cracker_group_options.add_argument(
        "--use-local", default=False, help="Use a local copy of Tensorflow model instead of CAPTCHA22", action="store_true")

    cracker_group_storage = cracker_parser.add_argument_group(
        title="Storage Arguments")

    # Storage var
    cracker_group_storage.add_argument(
        "--input", default="./input/", help="Specify the directory where solved CAPTCHAs are stored")
    cracker_group_storage.add_argument(
        "--output", default="./output/", help="Specify the output directory where new correct and incorrect CAPTCHAs are stored")

    cracker_group_images = cracker_parser.add_argument_group(
        title="CAPTCHA Image Arguments")

    # Image var
    cracker_group_images.add_argument(
        "--image-type", default="png", help="Specify the image file type, default is png")
    cracker_group_images.add_argument(
        "--filter-low", default=130, type=int, help="Grayscale lower limit for image filter, default is 130")
    cracker_group_images.add_argument(
        "--filter-high", default=142, type=int, help="Grayscale upper limit for image filter, default is 142")
    cracker_group_images.add_argument(
        "--captcha-id", default=None, help="Specify captchID from CATCHA22 API Server for the model that will be used, default will be prompted")

    cracker_group_pyppeteer = cracker_parser.add_argument_group(
        title="Pyppeteer Arguments")

    # Pyppeteer var
    cracker_group_pyppeteer.add_argument("--check-captcha", default="What code is in the image?",
                                         help="Specify the phrase that Pyppeteer can search for to determine if it is on the CAPTCHA page")
    cracker_group_pyppeteer.add_argument(
        "--check-login", default="Password", help="Specify the phrase that Pyppeteer can search for to determine if it is on the Login page")
    cracker_group_pyppeteer.add_argument("--verify-login", default="The user name or password you entered isn't correct. Try entering it again.",
                                         help="Specify the prhase that Pyppeteer can search for to determine if the login attempt     failed")
    cracker_group_pyppeteer.add_argument(
        "--username-field", default="username", help="Specify HTML field where the username entry is located")
    cracker_group_pyppeteer.add_argument(
        "--password-field", default="password", help="Specify HTML field where the password entry is located")
    cracker_group_pyppeteer.add_argument(
        "--captcha-field", default="ans", help="Specify HTML field where the CAPTCHA answer must be submitted")
    cracker_group_pyppeteer.add_argument(
        "--attacking-url", default=None, help="Specify the URL of the website that will be attacked")

    cracker_group_attack = cracker_parser.add_argument_group(
        title="Attack Arguments")

    # Attacking var
    cracker_group_attack.add_argument(
        "--username-file", default=None, help="Specify path to file containing usernames for brute force attack")
    cracker_group_attack.add_argument(
        "--password-file", default=None, help="Specify path to file containing passwords for brute force attack")

    #### SERVER ONLY ####
    server_server_parser = server_subparsers.add_parser(
        "engine", help="Use to execute the CAPTCHA22 Engine")
    server_server_parser.set_defaults(func=server)

    # Arguments
    parser_group_training = server_server_parser.add_argument_group(
        title="Training Arguments")

    parser_group_training.add_argument(
        "--max-steps", default=2000, type=int, help="Specify the maximum amount of training steps per CAPTCHA upload, default is 2000")
    parser_group_training.add_argument("--loss-threshold", default=0.0002, type=float,
                                       help="Specify the threshold of loss at which training should stop, default is 0.0002")
    parser_group_training.add_argument("--perplexity-threshold", default=1.00018,
                                       help="Specify the threshold of perplexity at which training should stop, default is 1.00018")
    parser_group_training.add_argument(
        "--split-percentage", default=90.0, type=float, help="Specify the data split percentage for training vs testing data, default is 90.0")

    parser_group_hosting = server_server_parser.add_argument_group(
        title="Model Hosting Arguments")

    parser_group_hosting.add_argument(
        "--starting-port", default=9000, type=int, help="Specify the starting port for new models to be hosted, default is 9000")

    parser_group_storage = server_server_parser.add_argument_group(
        title="Storage Arguments")

    parser_group_storage.add_argument("--model-file", default="models.txt", help="Specify the file that stores the location of all previous models, default is models.txt")

    parser_group_storage.add_argument("--input-folder", default="./Unsorted",
                                      help="Specify the folder that will be monitored for new uploads, default is ./Unsorted")
    parser_group_storage.add_argument("--work-folder", default="./Busy",
                                      help="Specify the folder where training data will be stored, default is ./Busy")
    parser_group_storage.add_argument("--model-folder", default="./Model",
                                      help="Specify the folder where CAPTCHA models will be stored, default is ./Models")

    #### API ONLY ####
    api_parser = server_subparsers.add_parser(
        "api", help="Use to execute the CAPTCHA22 API Server")
    api_parser.set_defaults(func=server_api)

    parser_group_hosting = api_parser.add_argument_group(
        title="Hosting Arguments")

    parser_group_hosting.add_argument(
        "--host", default="0.0.0.0", help="Specify host where the API would execute, default is 0.0.0.0")
    parser_group_hosting.add_argument(
        "--port", default="5000", help="Specify port where the API would execute, default is 5000")
    parser_group_hosting.add_argument(
        "--enable-debugging", default=False, help="Specify if the API service should execute in debug mode, default is False", action="store_true")

    parser_group_datastore = api_parser.add_argument_group(
        title="Datastore Arguments")

    parser_group_datastore.add_argument("--file-drop", default='./Unsorted/',
                                        help="Specify the folder where new CAPTCHA uploads should be stored for CAPTCHA22, default is ./Unsorted/")
    parser_group_datastore.add_argument(
        "--max-tokens", default=5, type=int, help="Specify the maximum amount of tokens allowed per use, default is 5")
    parser_group_datastore.add_argument(
        "--server-location", default='./', help="Specify the base folder of the CAPTCHA22 Server, default is ./")
    parser_group_datastore.add_argument(
        "--user-file", default='users.txt', help="Specify file where user credentials for API is stored, default is users.txt")
    parser_group_datastore.add_argument(
        "--work-folder", default="./Busy", help="Specify the folder where training data of CAPTCHA22 will be stored, default is ./Busy")
    parser_group_datastore.add_argument("--model-folder", default="./Model",
                                        help="Specify the folder where CAPTCHA models of CAPTCHA22 will be stored, default is ./Models")

    args = main_parser.parse_args()

    if len(sys.argv) == 1:
        main_parser.print_help(sys.stderr)
        sys.exit(1)

    if (args.func == client_help):
        client_parser.print_help(sys.stderr)
        sys.exit(1)

    if (args.func == server_help):
        server_parser.print_help(sys.stderr)
        sys.exit(1)

    try:
        args.func(args)
    except KeyboardInterrupt:
        sys.exit()


if __name__ == "__main__":
    main()
