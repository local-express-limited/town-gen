#!/usr/bin/python3

from string import ascii_lowercase
from lxml import html
import pathlib
import requests

raw_file = pathlib.Path('places_raw')

if not raw_file.is_file():
    with open(raw_file.name, 'w', encoding="utf-8") as f:
        # Download all places
        for alpha in ascii_lowercase:
            # Fetch and parse page for given letter
            url_eng = f"https://www.townscountiespostcodes.co.uk/towns-in-england/letter/{alpha}/"
            url_wal = f"https://www.townscountiespostcodes.co.uk/towns-in-wales/letter/{alpha}/"
            result = requests.get(url_eng, stream=True)
            result.raw.decode_content = True
            page = html.parse(result.raw)
            places = page.xpath("//div[@id='content']//table/tbody/tr[not(@class='dummy')]/td[2]/text()")
            # Append to file without duplicates
            for place in list(dict.fromkeys(places)):
                f.write(f"{place}\n")


