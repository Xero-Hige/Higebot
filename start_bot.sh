#!/usr/bin/env bash
export $(cat *.env | xargs)
python3 higebot.py