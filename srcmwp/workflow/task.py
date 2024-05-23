# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

from .flowData import FlowData;
from collections import OrderedDict;
from .flowData import Status;
from .util import convert_fieldname_to_db;

class Task(FlowData):
    '''
    Represents one task to complete
    '''

    def __init__(self, flowname, rolename, stepname, data=OrderedDict(), sequence=None, status=None, uid=None, parents=None):
        FlowData.__init__(self, flowname, rolename, stepname, data, sequence, status, uid, parents);
    
    @classmethod    
    def construct_from_result(cls, result, rolename, stepname, data=OrderedDict(), status=Status.NEW, uid=None, copy=True, parents=None):
        if parents == None:
            parents = result;
        instance = cls(result.flowname, rolename, stepname, data, result.sequence, status, uid, parents);
        if copy == True:
            copy = result.data.keys();
        if hasattr(copy, '__iter__'):
            # Put the existing data in first.
            temp = instance.data;
            instance.data = OrderedDict();
            for k in copy:
                k = convert_fieldname_to_db(k);
                if k in result.data:
                    instance.data[k] = result.data[k];
                else:
                    print("Error: unknown key: " + k);
            instance.data.update(temp);
        return instance;

    @classmethod    
    def construct_from_results(cls, results, rolename, stepname, data=OrderedDict(), status=Status.NEW, uid=None, copy=None, append=None, add_fields=None):
        # First copy everthing we are to copy, using result[0];
        instance = cls.construct_from_result(results[0], rolename, stepname, data, status, uid, copy, results);
        # Now handle appends:
        if append != None:
            for k in append:
                k = convert_fieldname_to_db(k);
                if k not in instance.data:
                    instance.data[k] = "";
                first = True;
                for result in results:
                    d = "";
                    if k in result.data:
                        d = result.data[k];
                    if d == None:
                        d = "";
                    if first:
                        first = False;
                    else:
                        instance.data[k] = instance.data[k] + ",";
                    instance.data[k] = instance.data[k] + str(d);                
        # Now handle adds:
        if add_fields != None:
            for k in add_fields:
                k = convert_fieldname_to_db(k);
                if k not in instance.data:
                    instance.set_field(k, 0);
                for result in results:
                    d = 0;
                    if k in result.data:
                        if d != None:
                            d = result.get_float_field(k);
                    instance.set_field(k, instance.get_float_field(k) + d);                
        return instance;

