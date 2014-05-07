#!/usr/bin/python

import sys
import re

tag_re = re.compile('\(([^\)]+)\)')

text = sys.argv[1]
text_tags = map(lambda m: m.group(1), tag_re.finditer(text))

sys.stdout.write(re.sub(tag_re, '', text))

all_tags_found = set(text_tags).issubset(set(sys.argv[2:]))
if all_tags_found:
    sys.exit(0)
else:
    sys.exit(1)
