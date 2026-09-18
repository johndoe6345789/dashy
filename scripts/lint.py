#!/usr/bin/env python3
"""Lint the Dashy configs: schema-valid, and free of the mistakes that
previously crept in (dead ports, private hostnames, duplicates, editor
leftovers).

usage: scripts/lint.py SCHEMA.json [conf.yml]
Pages listed under `pages:` in the main config are linted too.
"""
import json
import os
import re
import sys
from collections import Counter
from urllib.parse import urlsplit

import jsonschema
import yaml

# Cloudflare's proxy only forwards these ports; anything else on a proxied
# hostname can never load.
CF_HTTPS_PORTS = {443, 2053, 2083, 2087, 2096, 8443}
CF_HTTP_PORTS = {80, 8080, 8880, 2052, 2082, 2086, 2095}


def lint_file(path, validator):
    errors = []
    cfg = yaml.safe_load(open(path))
    for e in validator.iter_errors(cfg):
        errors.append(f"schema: /{'/'.join(map(str, e.path))}: {e.message}")

    items = [(s["name"], i) for s in cfg.get("sections", []) for i in s.get("items", [])]
    for url, n in Counter(i.get("url") for _, i in items).items():
        if n > 1:
            errors.append(f"duplicate url ({n}x): {url}")
    for (sec, title), n in Counter((s, i.get("title")) for s, i in items).items():
        if n > 1:
            errors.append(f"duplicate title in '{sec}' ({n}x): {title}")

    for sec, i in items:
        where = f"'{sec}' / '{i.get('title')}'"
        url = i.get("url", "")
        u = urlsplit(url)
        host = u.hostname or ""
        if not i.get("icon"):
            errors.append(f"{where}: no icon")
        if str(i.get("id", "")).startswith("temp_"):
            errors.append(f"{where}: leftover editor id {i['id']}")
        if host.endswith(".ts.net") or re.fullmatch(r"(10|100|127|172|192)\.[\d.]+", host):
            errors.append(f"{where}: private host in a public config: {url}")
        if host == "wardcrew.com" or host.endswith(".wardcrew.com"):
            if u.scheme != "https":
                errors.append(f"{where}: use https for wardcrew.com links: {url}")
            if u.port and u.port not in CF_HTTPS_PORTS | CF_HTTP_PORTS:
                errors.append(f"{where}: port {u.port} is not proxied by Cloudflare: {url}")
    return cfg, errors


def main():
    schema_path, root = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "conf.yml")
    validator = jsonschema.Draft7Validator(json.load(open(schema_path)))
    todo, seen, failed = [root], set(), False
    while todo:
        path = todo.pop()
        if path in seen:
            continue
        seen.add(path)
        if not os.path.exists(path):
            print(f"{path}: missing (listed under pages:)")
            failed = True
            continue
        cfg, errors = lint_file(path, validator)
        for p in cfg.get("pages") or []:
            todo.append(os.path.join(os.path.dirname(path), p["path"]))
        for e in errors:
            print(f"{path}: {e}")
        failed |= bool(errors)
        print(f"{path}: {'FAIL' if errors else 'ok'}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
