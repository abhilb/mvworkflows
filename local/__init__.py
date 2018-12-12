import glob
import os
import re
import yaml
import logging
logging.basicConfig(format="%(levelname)s - %(message)s", level="INFO")

Operators = {}

yaml_files = glob.glob("local/operators/*.yaml")
for filename in yaml_files:
    pattern = re.compile(r"(\w+).yaml")
    match = pattern.search(filename)
    operator_name = ""
    if match:
        operator_name = match.group(1)

    if len(operator_name) > 0:
        with open(filename, "r") as f:
            Operators[operator_name] = yaml.safe_load(f)

