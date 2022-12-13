import re

# Should not match
string1 = "SimeonKostadinov.0141_-"

# Should match
string2 = 'SimeonKostadinov+0141*'

pattern = re.compile('[^a-zA-Z0-9\._-]')

if pattern.match(string1): print('string1 matches pattern.(match)')
if pattern.match(string2): print('string2 matches pattern.(match)')
if pattern.search(string1): print('string1 matches pattern.(search)')
if pattern.search(string2): print('string2 matches pattern.(search)')