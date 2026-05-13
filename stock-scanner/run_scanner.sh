#!/bin/bash
cd "$(dirname "$0")"
.venv/bin/python main.py >> logs/scanner.log 2>&1
