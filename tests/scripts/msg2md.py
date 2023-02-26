#!/usr/bin/python3

import fileinput
import json
import textwrap

def process_debug_log(line):
    pre, msg = line.split(" | ")
    _, _, msg_from, _, msg_to = pre.split()

    print(f"**From**: {msg_from}")
    print(f"\n**To**: {msg_to}")
    print("\n**Message**:\n\n")

    msg_json = json.loads(msg)
    msg_txt = json.dumps(msg_json, indent=2)
    msg_txt = textwrap.indent(msg_txt, "    ")
    print(msg_txt)
    print("\n")

if __name__ == "__main__":
    for line in fileinput.input():
        if line.startswith("DEBUG    messaging"):
            process_debug_log(line)