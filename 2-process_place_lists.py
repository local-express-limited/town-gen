#!/usr/bin/python3

import pathlib
import re

# Things we don't care about:
# - alternate names in brackets
reAlt = re.compile('^(.*) \\(.*\\)$')
# - definite articles
reDef = re.compile('(^The,? .*$|^.*,? The$)')
# - bodies of water
reCanal = re.compile('^.*[ -](Beck|Bec|Drain|Channel|Canal|[Bb]rook|Ford|Lea|Lee|Quay|Cove|Reservoir|Navigation|Water|Waterways|Pool|Wharfe?|Lake)(,.*)?$')
reLeCanal = re.compile('^.*the[ -]Water$')
# - model villages, inns, country houses
reModel = re.compile('^.*(Model Village| Inn| Hall| Estate| Shop| Cottage| Cottages| ddu| Ho!| Allotments?)$')
# - islands
reIsle = re.compile('(^Isl(and|e)s? .*$|^.*Isl(and|e)$)')
# - saint names
reSaintSuf = re.compile('^(.*)(-in-| )St[ .][A-Z][a-z].*$')
reAllSaintSuf = re.compile('^(.*)[ -]All[ -]Saints.*$')
reSaint = re.compile('(^St\\.? .*$|^Saint .*$|^All Saints.*$)')
# - street names
reStreet = re.compile(r'^.*\b(Highway|Grove|Crescent|Bank|Square|Sq|Common|Grange|Garden|Gardens|Gdns|Road|Mount|[Hh]ill|Row|[Gg]ate|Terrace|Place|Court|Green|Park|Rise|Lane|St|Street)$')
reLeStreet = re.compile('^.*[ -][Ll]e[ -](St|Street)$')
reLeHill = re.compile('^.*[ -]([uU]nder|[oO]n[ -][tT]he)[ -][hH]ill$')
# - rail related
reRail = re.compile(r'^.*\b(Central|Junction|Station|Sta|Halt|Line|Centre)\b.*$')
# - pub names
rePub = re.compile('^.*( & | and |-to-).*$')
# - "village" in the village name
reVillage = re.compile(r'^.*\b(City|Town|Towns|Village|Suburb)\b.*$')
# - incorrect capitalisation
reCaps = re.compile(r'^(.*)\b(allt|cefn|clawdd|coed|hill|edge|end|glas|holms|kiln|newydd|severn|thames|trees|llwyn|wra|wolds)\b(.*)$')
# - welsh
reWelsh = re.compile(r'^.*([Cc]oed|Ll|[ -]yr?[ -]|Pentre|Cwm|[Cc]roes|Allt).*$')

raw_file = pathlib.Path('places_raw')
processed_file = pathlib.Path('places_processed')

if not processed_file.is_file():
    # Read in raw place names
    with open(raw_file.name, encoding="utf-8") as rf:
        places = rf.read().split('\n')
    # Process place names for consistency
    with open(processed_file.name, 'w', encoding="utf-8") as pf:
        normalised_places = []
        for place in places:
            if not place:
                continue
            # Alterations
            if reAlt.match(place):
                old_place = place
                place = re.sub(reAlt, r'\1', place)
                #print(f"Fixed (alternate) : {old_place} >> {place}")
            if reSaintSuf.match(place):
                old_place = place
                place = re.sub(reSaintSuf, r'\1', place)
                #print(f"Fixed (saint)     : {old_place} >> {place}")
            if reAllSaintSuf.match(place):
                old_place = place
                place = re.sub(reAllSaintSuf, r'\1', place)
                #print(f"Fixed (saint)     : {old_place} >> {place}")
            if reCaps.match(place):
                old_place = place
                place = re.sub(reCaps, lambda m: m.group(1) + m.group(2).title() + m.group(3), place)
                print(f"Fixed (caps)      : {old_place} >> {place}")
            # Rejections
            if reDef.match(place):
                #print(f"Rejected (def art): {place}")
                continue
            if reCanal.match(place):
                if not reLeCanal.match(place):
                    #print(f"Rejected (water)  : {place}")
                    continue
                #print(place)
            if reModel.match(place):
                #print(f"Rejected (attract): {place}")
                continue
            if reIsle.match(place):
                #print(f"Rejected (island) : {place}")
                continue
            if reSaint.match(place):
                #print(f"Rejected (saint)  : {place}")
                continue
            if reStreet.match(place):
                if not reLeStreet.match(place) and not reLeHill.match(place):
                    #print(f"Rejected (street) : {place}")
                    continue
                #print(place)
            if reRail.match(place):
                #print(f"Rejected (rail)   : {place}")
                continue
            if rePub.match(place):
                #print(f"Rejected (pub)    : {place}")
                continue
            if reVillage.match(place):
                #print(f"Rejected (village): {place}")
                continue
            if reWelsh.match(place):
                #print(f"Rejected (welsh)  : {place}")
                continue
            # Normalise punctuation and capitalisation
            place = re.sub(r'[,\']', '', place)
            place = re.sub('-', ' ', place)
                           
            place = re.sub(r'\b[A-Z][A-Z]+\b', lambda m: m.group(0).title(), place)
            place = re.sub(' (yr?) (.)', lambda m: " {} {}".format(m.group(1), m.group(2).upper()), place)
            place = re.sub(' (Cum|Up|Over|Next The|Next|Upon|Under|Le|On The|On|In|Sub|Juxta|By The|By|The|Of) ',
                           lambda m: m.group(0).lower(), place)
            normalised_places.append(place)
        # Append to file without duplicates
        for place in list(dict.fromkeys(normalised_places)):
            pf.write(f"{place}\n")


