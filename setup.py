import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "chatter",
    version = "0.1",
    author = "Steve Winton",
    author_email = "steve.winton@nixonmcinnes.co.uk",
    description = ("The minimalist yet fully featured Chatter API class, heavily inspired by Python Twitter Tools.",),
    license = "MIT",
    keywords = "chatter api salesforce",
    url = "https://github.com/nixmc/chatter",
    packages=['chatter',],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
    ],
)