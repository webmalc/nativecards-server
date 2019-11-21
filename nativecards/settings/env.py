"""
The environment module
"""
import os

import environ

ROOT = environ.Path(__file__) - 3
ENV = environ.Env()

RUN_ENV = ENV.str('RUN_ENV', default='')

ENV_FILE = '.env_' + RUN_ENV if RUN_ENV else '.env'
environ.Env.read_env(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ENV_FILE))
