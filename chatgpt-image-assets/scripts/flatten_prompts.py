"""Flatten a tagged prompt file into one-line prompts.

Usage: python flatten_prompts.py <prompts.md> [out.json]

Sections start with "## <tag> · <Name>". Typing a newline into the ChatGPT
composer sends the message, so each prompt body is joined into one line.
Prints "<tag> :: <prompt>" per tag and writes {tag: prompt} as JSON if out is given.
"""
import json
import re
import sys


def flatten(path):
    text = open(path, encoding="utf-8").read()
    prompts = {}
    for part in re.split(r"^## ", text, flags=re.M)[1:]:
        head, _, body = part.partition("\n")
        tag = head.split()[0]
        lines = [line.strip() for line in body.strip().splitlines()]
        prompts[tag] = " ".join(line for line in lines if line and line != "---")
    return prompts


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    result = flatten(sys.argv[1])
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=1)
    for tag, prompt in result.items():
        print(f"{tag} :: {prompt}")
