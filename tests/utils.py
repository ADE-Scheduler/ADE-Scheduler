# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 ADE-Scheduler.
#
# ADE-Scheduler is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for tests."""

import json


def get_json(response):
    """Get JSON from response."""
    return json.loads(response.get_data(as_text=True))
