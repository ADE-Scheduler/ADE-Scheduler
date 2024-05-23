# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 ADE-Scheduler.
#
# ADE-Scheduler is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration for tests."""

import os
import sys

from dotenv import find_dotenv, load_dotenv

sys.path.append(os.getcwd())
load_dotenv(find_dotenv(".flaskenv"))
