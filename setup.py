import os
from setuptools import setup

setup(
    name = "chatter",
    version = "0.1.3",
    author = "Steve Winton",
    author_email = "steve.winton@nixonmcinnes.co.uk",
    description = ("The minimalist yet fully featured Chatter API class, heavily inspired by Python Twitter Tools.",),
    license = "MIT",
    keywords = "chatter api salesforce",
    url = "https://github.com/nixmc/chatter",
    packages=['chatter',],
    long_description=open("./README", "r").read(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=[
        'urllib3>=1.3'
    ]
    include_package_data=True,
    zip_safe=True,
)