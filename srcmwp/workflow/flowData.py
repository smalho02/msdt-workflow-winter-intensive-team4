# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 17, 2012
@author: blubin
'''

from collections import OrderedDict;
from collections import namedtuple;
from .util import enum;
from .util import convert_fieldname_to_db;
from .util import convert_flowname_to_db;
from .util import convert_rolename_to_db;
from .util import convert_stepname_to_db;

Status = enum('NEW', 'COMPLETE');

FlowDataReferenceT = namedtuple("FlowDataReference", "rolename stepname type uid");

class FlowDataReference(FlowDataReferenceT):
    
    def __init__(self, **kwargs):
        FlowDataReferenceT.__init__(self)
    
    @classmethod
    def to_string(cls, ref):
        if isinstance(ref, str):
            #Assume the string is already ok:
            return ref;
        return ref.rolename + "|" + ref.stepname + "|" + ref.type+ "|" + str(ref.uid);

    @classmethod
    def from_string(cls, string):
        splits = string.split("|");
        if len(splits) != 4:
            raise Exception("Incorrect format: " + string);
        return FlowDataReference(rolename = splits[0], stepname = splits[1], type = splits[2], uid = int(splits[3]));

    @classmethod
    def from_flow_data(cls, flowData):
        return FlowDataReference(rolename = flowData.rolename, stepname = flowData.stepname, type = flowData.__class__.__name__, uid = flowData.uid);
 
    @classmethod
    def from_unknown(cls, p):
        if isinstance(p, FlowDataReference):
            return p;
        elif isinstance(p, str):
            return FlowDataReference.from_string(p);
        else:
            return FlowDataReference.from_flow_data(p);

class FlowData(object):
    '''
    Abstract base class for data in the workflow
    '''
    
    def __init__(self, flowname, rolename, stepname, data=OrderedDict(), sequence=None, status=Status.NEW, uid=None, parents=None):
        self.flowname = convert_flowname_to_db(flowname);
        self.rolename = convert_rolename_to_db(rolename);
        self.stepname = convert_stepname_to_db(stepname);
        self.data = data;
        self.sequence = sequence;
        self.status = status;
        self.uid = uid;
        #Store the parent information:
        if parents == None:
            self.parents = None;
        else:
            if not isinstance(parents, list):
                self.set_parents([parents]);
            else:
                self.set_parents(parents);
        
    def set_parents(self, parents):
        self.parents = [FlowDataReference.from_unknown(p) for p in parents];
                
    def set_field(self, fieldname, value):
        self.data[convert_fieldname_to_db(fieldname)] = value;
        
    def get_field(self, fieldname):    
        f = convert_fieldname_to_db(fieldname);
        if f=='flowname':
            return self.flowname;
        if f=='rolename':
            return self.rolename;
        if f=='stepname':
            return self.stepname;
        if f=='sequence':
            return self.sequence;
        if f=='status':
            return self.status;
        if f=='uid':
            return self.uid;
        else:
            return self.data[f];
        
    def get_str_field(self, fieldname):
        return self.data[convert_fieldname_to_db(fieldname)];

    def get_int_field(self, fieldname):
        return int(self.data[convert_fieldname_to_db(fieldname)]);

    def get_float_field(self, fieldname):
        return float(self.data[convert_fieldname_to_db(fieldname)]);

    def get_bool_field(self, fieldname):
        s = self.data[convert_fieldname_to_db(fieldname)];
        return s in ['TRUE', 'True', 'true', 'T', 't', '1', 1];

    def remove_field(self, fieldname):
        del self.data[convert_fieldname_to_db(fieldname)];
        
    def __eq__(self, other):
        if other == None:
            return False;
        if self.__class__ != other.__class__:
            return False;
        if self.uid != other.uid:
            return False;
        if self.flowname != other.flowname:
            return False;
        if self.rolename != other.rolename:
            return False;
        if self.stepname != other.stepname:
            return False;
        if self.sequence != other.sequence:
            return False;
        if self.status != other.status:
            return False;
        if self.parents != other.parents:
            return False;
        if self.data != other.data:
            return False;
        return True;
    
    def __ne__(self, other):
        return not self.__eq__(other);

    def __str__(self):
        s = '[' + self.__class__.__name__ + ' ';
        if self.sequence != None:
            s += str(self.sequence) +"#";

        if self.uid == None:
            uid = "None";
        else:
            uid = self.uid;
        s = s + str(uid) + " ";

        if self.status == None:
            stat = "None";
        else:
            stat = Status.reverse_mapping[self.status];
        s = s + ":" + stat + ": ";


        s = s + self.flowname + "." + self.rolename + "." + self.stepname + " ";
        
        
        dstr = ','.join(['%s:%s' % (key, value) for (key, value) in self.data.items()]);
        s = s + "(" + dstr + ") ";
        if self.parents == None:
            pstr = "";
        else:
            pstr = ','.join([FlowDataReference.to_string(k) for k in self.parents]);
        s = s + " (" + pstr + ")";
        s = s + "]";
        return s;
    