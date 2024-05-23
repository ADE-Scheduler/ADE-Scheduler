#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 ADE-Scheduler.
#
# ITLD is free software; you can redistribute it and/or modify it under the
# terms of the MIT License; see LICENSE file for more details.


# Quit on errors
set -o errexit

# COLORS for messages
NC='\033[0m'                    # Default color
INFO_COLOR='\033[1;97;44m'      # Bold + white + blue background
SUCCESS_COLOR='\033[1;97;42m'   # Bold + white + green background
ERROR_COLOR='\033[1;97;41m'     # Bold + white + red background

PROGRAM=`basename $0`
SCRIPT_PATH=$(dirname "$0")

# MESSAGES
msg() {
  echo -e "${1}" 1>&2
}
# Display a colored message
# More info: https://misc.flogisoft.com/bash/tip_colors_and_formatting
# $1: choosen color
# $2: title
# $3: the message
colored_msg() {
  msg "${1}[${2}]: ${3}${NC}"
}

info_msg() {
  colored_msg "${INFO_COLOR}" "INFO" "${1}"
}

error_msg() {
  colored_msg "${ERROR_COLOR}" "ERROR" "${1}"
}

error_msg+exit() {
    error_msg "${1}" && exit 1
}

success_msg() {
  colored_msg "${SUCCESS_COLOR}" "SUCCESS" "${1}"
}

success_msg+exit() {
  colored_msg "${SUCCESS_COLOR}" "SUCCESS" "${1}" && exit 0
}

# Displays program name
msg "PROGRAM: ${PROGRAM}"

# Poetry is a mandatory condition to launch this program!
if [[ -z "${VIRTUAL_ENV}" ]]; then
  error_msg+exit "Error - Launch this script via poetry command:\n\tpoetry run ${PROGRAM}"
fi

function pretests () {
  info_msg "Test pydocstyle:"
  pydocstyle tests/api docs
  info_msg "Test isort:"
  isort --check-only --diff tests
  info_msg "Test useless imports:"
  autoflake -c -r --remove-all-unused-imports --ignore-init-module-imports . &> /dev/null || {
      autoflake --remove-all-unused-imports -r --ignore-init-module-imports .
      exit 1
    }
}

function pre_commit () {
  pre-commit run --all-files
}

function tests () {
  info_msg "Tests All:"
  poetry run pytest --disable-warnings --cache-clear
}

function tests_api () {
  info_msg "Tests API:"
  poetry run pytest ./tests/api --disable-warnings --cache-clear
}

if [ $# -eq 0 ]
  then
    set -e
    pretests
    tests
fi

if [ "$1" = "tests" ]
  then
    set -e
    tests
fi

if [ "$1" = "api" ]
  then
    set -e
    tests_api
fi

if [ "$1" = "pre-commit" ]
  then
    set -e
    pre_commit
fi


success_msg+exit "Perfect ${PROGRAM} external! See you soon…"
