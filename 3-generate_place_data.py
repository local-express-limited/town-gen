#!/usr/bin/python3

import pathlib
import re
import json

from lark import Lark
from lark.visitors import Transformer

processed_file = pathlib.Path('places_processed')
json_file = pathlib.Path('places.json')

# Load syntax grammars
with open('grammar_places', encoding="utf-8") as g:
    grammar_places = g.read()
parser_places = Lark(grammar_places, start='place', parser='earley', lexer='dynamic', ambiguity='resolve')
with open('grammar_names', encoding="utf-8") as g:
    grammar_names = g.read()
parser_names = Lark(grammar_names, start='name', parser='earley', lexer='dynamic', ambiguity='resolve')

# Util to increment a counter in a table
def _inc(table, key):
    if key not in table:
        table[key] = 1
    else:
        table[key] = table[key] + 1

class TokenCounter(Transformer):
    def __init__(self, verbose=True):
        super().__init__(visit_tokens=True)
        self.verbose = verbose
        self.total_places = 0

        self.infix_places = 0
        self.infix_freq = {}

        self.all_names = []

        # The current place
        self.curr_prefix = ""
        self.curr_infix = ""
        self.curr_suffix = ""

        # Counts of total parts and part types in the prefix
        self.pre_partnum_freq = {}
        self.pre_headnum_freq = {}
        self.pre_namenum_freq = {}
        self.pre_tailnum_freq = {}
        # Counts of total parts and part types in the suffix
        self.suf_partnum_freq = {}
        self.suf_headnum_freq = {}
        self.suf_namenum_freq = {}
        self.suf_tailnum_freq = {}

        # Occurance frequencies of heads and tails
        self.pre_head_freq = {}
        self.pre_tail_freq = {}
        self.suf_head_freq = {}
        self.suf_tail_freq = {}
        
        # Reset current number of parts count
        self._reset_part_num_count()

    def _reset_part_num_count(self, prefix_done=False, suffix_done=False):
        # Update counts of total parts and part types in the prefix
        if prefix_done:
            _inc(self.pre_partnum_freq, len(self.heads) + self.namenum + len(self.tails))
            _inc(self.pre_headnum_freq, len(self.heads))
            _inc(self.pre_namenum_freq, self.namenum)
            _inc(self.pre_tailnum_freq, len(self.tails))
            for head in self.heads:
                _inc(self.pre_head_freq, head)
            for tail in self.tails:
                _inc(self.pre_tail_freq, tail)
        # Update counts of total parts and part types in the suffix
        if suffix_done:
            _inc(self.suf_partnum_freq, len(self.heads) + self.namenum + len(self.tails))
            _inc(self.suf_headnum_freq, len(self.heads))
            _inc(self.suf_namenum_freq, self.namenum)
            _inc(self.suf_tailnum_freq, len(self.tails))
            for head in self.heads:
                _inc(self.suf_head_freq, head)
            for tail in self.tails:
                _inc(self.suf_tail_freq, tail)
        # Reset counts
        self.heads = []
        self.namenum = 0
        self.tails = []

    def place(self, children):
        self.total_places = self.total_places + 1

        # Reset the current place strings
        if self.curr_infix:
            _inc(self.infix_freq, self.curr_infix)
            if self.verbose:
                print(self.curr_prefix + f" INFIX {self.curr_infix} " + self.curr_suffix)
        else:
            _inc(self.infix_freq, "")
            if self.verbose:
                print(self.curr_prefix)
        self.curr_prefix = ""
        self.curr_infix = ""
        self.curr_suffix = ""

        # Reset current number of parts count
        self._reset_part_num_count()

    def HEAD(self, token):
        self.heads.append(token.value)
        return token
    def NAME(self, token):
        self.namenum = self.namenum + 1
        self.all_names.append(token.value)
        return token
    def TAIL(self, token):
        self.tails.append(token.value)
        return token

    def prefix(self, children):
        self.curr_prefix = ""
        for child in children:
            if self.curr_prefix:
                self.curr_prefix = f"{self.curr_prefix} {child.type} {child.value}"
            else:
                self.curr_prefix = f"{child.type} {child.value}"
        # Reset current number of parts count
        self._reset_part_num_count(prefix_done=True)

    def infix(self, children):
        self.infix_places = self.infix_places + 1
        self.curr_infix = "-"
        for child in children:
            self.curr_infix = f"{self.curr_infix}{child.value}-"

    def suffix(self, children):
        self.curr_suffix = ""
        for child in children:
            if self.curr_suffix:
                self.curr_suffix = f"{self.curr_suffix} {child.type} {child.value}"
            else:
                self.curr_suffix = f"{child.type} {child.value}"
        # Reset current number of parts count
        self._reset_part_num_count(suffix_done=True)

    def get_all_names(self):
        return sorted(list(set(self.all_names)))

    def get_prefix_data(self):
        data = {}
        data["num_heads"] = self.pre_headnum_freq
        data["num_names"] = self.pre_namenum_freq
        data["num_tails"] = self.pre_tailnum_freq
        data["heads"] = dict(reversed(sorted(self.pre_head_freq.items(), key = lambda x: x[1])))
        data["tails"] = dict(reversed(sorted(self.pre_tail_freq.items(), key = lambda x: x[1])))
        return data

    def get_infix_data(self):
        return dict(reversed(sorted(self.infix_freq.items(), key = lambda x: x[1])))

    def get_suffix_data(self):
        data = {}
        data["num_heads"] = self.suf_headnum_freq
        data["num_names"] = self.suf_namenum_freq
        data["num_tails"] = self.suf_tailnum_freq
        data["heads"] = dict(reversed(sorted(self.suf_head_freq.items(), key = lambda x: x[1])))
        data["tails"] = dict(reversed(sorted(self.suf_tail_freq.items(), key = lambda x: x[1])))
        return data


class NameChunker(Transformer):
    def __init__(self, verbose=True):
        super().__init__(visit_tokens=True)
        self.verbose = verbose
        self.total_names = 0
        
        self.all_starts = []

        # Occurrance frequency of ends chunks
        self.end_freq = {}
        # Number of end chunks frequency
        self.endnum_freq = {}

        # Reset for next name
        self.start_chunk = ""
        self.end_chunks = []

    def name(self, children):
        self.total_names = self.total_names + 1

        if self.verbose:
            if self.end_chunks:
                print(f"START {self.start_chunk}", end='')
                for end in reversed(self.end_chunks):
                    print(f" END {end}", end='')
                print()
            else:
                print(f"START {self.start_chunk}")

        # Log how many end chunks this name has
        _inc(self.endnum_freq, len(self.end_chunks))

        # Log occurance and position of each end chunk
        for i, end_chunk in list(enumerate(self.end_chunks, start=1)):
            if end_chunk not in self.end_freq:
                self.end_freq[end_chunk] = {}
            stats = self.end_freq[end_chunk]
            _inc(stats, i)

        # Reset for next name
        self.start_chunk = ""
        self.end_chunks = []

    def START(self, token):
        val = token.value[::-1]
        # Log the occurrance of this start
        self.start_chunk = val
        self.all_starts.append(val)
        return token

    def END(self, token):
        val = token.value[::-1]
        # Log the occurrance of this end
        self.end_chunks.append(val)
        return token

    def get_unique_starts(self):
        # Sorted list of all unique starts
        return sorted(list(set(self.all_starts)))

    def get_data(self):
        data = {}
        data["starts"] = self.get_unique_starts()
        data["num_ends"] = self.endnum_freq
        data["ends"] = {}
        for key in self.end_freq:
            stats = self.end_freq[key]
            for pos in stats:
                if pos not in data["ends"]:
                    data["ends"][pos] = {}
                data["ends"][pos][key] = stats[pos]
        return data


counter = TokenCounter(verbose=False)
chunker = NameChunker(verbose=False)

with open(processed_file.name, encoding="utf-8") as f:
    places = [line for line in f.read().splitlines() if line]

for place in places:
    tree = parser_places.parse(place)
    counter.transform(tree)

for name in counter.get_all_names():
    tree = parser_names.parse(name[::-1])
    chunker.transform(tree)

json_data = {}
json_data["names"] = chunker.get_data()
json_data["prefixes"] = counter.get_prefix_data()
json_data["infixes"] = counter.get_infix_data()
json_data["suffixes"] = counter.get_suffix_data()

if json_file.is_file():
    json_file.unlink()
with open(json_file.name, 'w', encoding="utf-8") as jf:
    json.dump(json_data, jf, indent=2)

print(f"Total unique places: {counter.total_places}")
print(f"Total infixed places: {counter.infix_places}")
print(f"Infix frequency:")
for key in counter.get_infix_data():
    value = counter.get_infix_data()[key]
    print(f"  {key}: {value}")
print()
print(f"Total number of parts in prefixes:")
for key in sorted(counter.pre_partnum_freq):
    print(f"  {key}: {counter.pre_partnum_freq[key]}")
print(f"Prefix Composition:")
print(f"  Number of head parts:")
for key in sorted(counter.pre_headnum_freq):
    print(f"    {key}: {counter.pre_headnum_freq[key]}")
print(f"  Number of name parts:")
for key in sorted(counter.pre_namenum_freq):
    print(f"    {key}: {counter.pre_namenum_freq[key]}")
print(f"  Number of tail parts:")
for key in sorted(counter.pre_tailnum_freq):
    print(f"    {key}: {counter.pre_tailnum_freq[key]}")
print(f"Total number of parts in suffixes:")
for key in sorted(counter.suf_partnum_freq):
    print(f"  {key}: {counter.suf_partnum_freq[key]}")
print(f"Suffix Composition:")
print(f"  Number of head parts:")
for key in sorted(counter.suf_headnum_freq):
    print(f"    {key}: {counter.suf_headnum_freq[key]}")
print(f"  Number of name parts:")
for key in sorted(counter.suf_namenum_freq):
    print(f"    {key}: {counter.suf_namenum_freq[key]}")
print(f"  Number of tail parts:")
for key in sorted(counter.suf_tailnum_freq):
    print(f"    {key}: {counter.suf_tailnum_freq[key]}")
print()
print(f"Total unique names: {chunker.total_names}")
num_starts = len(chunker.get_unique_starts())
print(f"Unique start chunks: {num_starts}")
print(f"Number of end chunks frequency:")
for key in sorted(chunker.endnum_freq):
    print(f"  {key}: {chunker.endnum_freq[key]}")


#print(f"Head part frequency:")
#for key, value in reversed(sorted(counter.head_freq.items(), key = lambda x: x[1])):
#    print(f"  {key}: {value}")
#print(f"Name frequency:")
#for key, value in reversed(sorted(counter.name_freq.items(), key = lambda x: x[1])):
#    if value > 5:
#        print(f"  {key}: {value}")

