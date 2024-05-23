# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

import re

# Define an enum type, per: http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-enum-in-python
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.items())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

def convert_flowname_to_db(flowname):
    return to_alpha_numeric(flowname, label="flowname");

def convert_rolename_to_db(rolename):
    return to_alpha_numeric(rolename, label="rolename");

def convert_stepname_to_db(stepname):
    return to_alpha_numeric(stepname, label="stepname");

def convert_fieldname_to_db(fieldname):
    return to_alpha_numeric(fieldname, "fieldname");

def to_alpha_numeric(string, label=""):
    if not string.isalnum():
        print("Warning: "+label+" should only contain alphanumeric characters: " + string);
    #string = filter(str.isalnum, string);
    string = re.sub(r'\W+','',string)
    if len(string) == 0:
        raise Exception(label+" must have non-zero length: " + string);
    return string;
