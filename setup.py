from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = ['pytest','aocr', 'numpy', 'opencv-python', 'Flask', 'flask_restful', 'flask_httpauth', 'pytest-shutil', 'pillow', 'pyppeteer']
VERSION = 'v1.0.2'

setup(
    name='captcha22',
    url='https://github.com/FSecureLABS/captcha22/',
    download_url='https://github.com/FSecureLABS/captcha22/archive/{}.tar.gz'.format(VERSION),
    author='Tinus Green',
    author_email='work@tinusgreen.co.za',
    version=VERSION,
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description=('''CAPTCHA Cracking Server and Client based '''
                 '''on Tensorflow, attention-ocr and Flask. '''),
    entry_points={
        'console_scripts': ['captcha22=captcha22.__main__:main'],
    }
)
