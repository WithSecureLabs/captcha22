#!/usr/bin/python3
import sys
import argparse

# Import libs

# Helper classes
#from lib.helpers.renamer import EntryWindow
#from lib.helpers.captcha_labelling import CaptchaLabeller
#from lib.helpers.label_generator import LabelGenerator

# API classes
#from lib.api.captcha22_client import client, menu
#from lib.crackers.captcha_solve import Client, Menu

# Cracker classes
# from lib.crackers.captcha_solve import
# from lib.crackers.captcha_cracking import
# from lib.crackers.pyppeteer_cracking import
#from lib.crackers.captcha_cracking import Cracker
#from lib.crackers.pyppeteer_cracking import *

#### HELPERS ####
# Execute the captcha Typer


def captcha_typer(args):
    import tkinter
    from lib.labels.labeller import EntryWindow
    root = tkinter.Tk()
    entry_window = EntryWindow(root, args.input, args.output, args.image_type)
    root.title = "F-Secure Captcha Renamer"
    entry_window.mainloop()

# Execute the legacy captcha Labeller


def captcha_labeller(args):
    from lib.labels.labeller_legacy import CaptchaLabeller
    labeller = CaptchaLabeller(args.input, args.output, args.image_type)
    labeller.main()

# Execute the AOCR label generator


def label_generator(args):
    from lib.labels.generator import LabelGenerator
    generator = LabelGenerator(args.input, args.output, args.image_type)
    generator.main()

# Function to use the labelling scripts to label your captchas


def label(args):
    if args.script == None:
        raise argparse.ArgumentTypeError("script has to be provided")

    if args.script == "captchaTyper":
        print("Executing CAPTCHA Typing Script")
        captcha_typer(args)
    elif args.script == "captchaLabeller":
        print("Executing Legacy CAPTCHA Typing Script")
        captcha_labeller(args)
    elif args.script == "labelGenerator":
        print("Executing AOCR Label Generator")
        label_generator(args)
    else:
        raise argparse.ArgumentTypeError(
            "script '{args.script}' is not a valid option")

#### APIs ####


def api_full(args):
    from lib.api.client import Menu
    new_menu = Menu(args.server_url, args.server_path, args.server_port, args.username, args.password)
    new_menu.main()


def api_basic(args):
    from lib.api.captcha_solve import Menu
    new_menu = Menu(args.server_url, args.server_path, args.server_port, args.input, args.image_type, args.captcha_id, args.username, args.password)
    new_menu.main()

# Function to use the API scripts to interface with CAPTCHA22


def client_api(args):
    if args.script == "full":
        print("Executing Full CAPTCHA22 API Client")
        api_full(args)
    elif args.script == "basic":
        print("Executing Basic CAPTCHA22 API Client")
        api_basic(args)
    else:
        raise argparse.ArgumentTypeError(
            "script '{args.script} is not a valid option'")

#### CRACKERS ####


def cracker_baseline(args):
    from lib.crackers.captcha import Cracker
    temp_cracker = Cracker(args.server_url, args.server_path, args.server_port, args.username, args.password,
                           args.max_session_duration, args.use_hashes, args.use_filter, args.use_local, args.input,
                           args.output, args.image_type, args.filter_low, args.filter_high, args.captcha_id)
    temp_cracker.main()


def cracker_pyppeteer(args):
    from lib.crackers.pyppeteer import PyppeteerCracker
    puppet = PyppeteerCracker(args.server_url, args.server_path, args.server_port, args.username, args.password,
                              args.max_session_duration, args.use_hashes, args.use_filter, args.use_local, args.input, args.output,
                              args.image_type, args.filter_low, args.filter_high, args.captcha_id, args.check_captcha,
                              args.check_login, args.verify_login, args.username_field, args.password_field, args.captcha_field,
                              args.attacking_url, args.username_file, args.password_file)
    puppet.norm_main()

# Function to use the Cracker scripts to crack captchas


def cracker(args):
    if args.script == "baseline":
        print("Executing Baseline Cracker Script")
        cracker_baseline(args)
    elif args.script == "pyppeteer":
        print("Executing Pyppeteer Cracker Script")
        cracker_pyppeteer(args)
    else:
        raise argparse.ArgumentTypeError(
            "script '{args.script} is not a valid option'")


if __name__ == "__main__":
    print ("Please use captcha22 from terminal")
