# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name="restretto",
    version="1.0.6",
    description="restretto is REST API testing tool",
    long_description="YML-scenario based REST API testing tool",
    author="Arthur Orlov",
    author_email="feature.creature@gmail.com",
    url="http://github.com/wirewit/restretto",
    license="",
    packages=find_packages(),
    entry_points={"console_scripts": ["restretto = restretto.cli:main"]},
    install_requires=["requests>=2.7.0", "pyaml>=3.11", "jinja2>=2.8", "clint>=0.5"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: Apache Software License"
    ]
)
