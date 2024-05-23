# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 21, 2012
@author: blubin
'''

from flowData import Status;
from util import convert_rolename_to_db;
from util import convert_stepname_to_db;

class GoogleJoinedListener(object):
    '''
    Listen to one or more result tables, and fires when predicate says so.  
    Note: bins by 'sequence' field; you only get results associated with the same sequence number 
    '''

    def __init__(self, googleDB, listenlist, predicate, listener):
        '''
        Arguments:
        googleDB, the db to attach to.
        listenlist: a list of tuples, each of the form (rolename, stepname, flowDataCls, status) to listen to.  FlowDataCls is Task or Result, If omitted, status defaults to Status.NEW
        predicate: a function, that takes a set of results obtained so far.  return True iff the set is complete and the event should fire.
        listener: the function to fire.  it takes a list of the results.
        '''
        self.seqdata = {}; #dictionary of sequence->list of unproceessed flowData instances.
        self.predicate = predicate;
        self.listener = listener;
        for t in listenlist:
            rolename = convert_rolename_to_db(t[0]);
            stepname = convert_stepname_to_db(t[1]);
            flowDataCls = t[2];
            if len(t) == 4:
                status = t[3];
            else:
                status = Status.NEW;
            googleDB.register_listener(rolename, stepname, flowDataCls, self.handler, status);
    
    def handler(self, data):
        sequences = self.add_data(data);
        for seq in sequences:
            d = self.seqdata[seq];
            if self.predicate(d):
                self.listener(d);
                del self.seqdata[seq];
            
    def add_data(self, flowData):
        ret = set();
        for d in flowData:
            seq = d.sequence;
            if seq not in self.seqdata:
                self.seqdata[seq]=[];
            self.seqdata[seq].append(d);
            ret.add(seq);
        return ret;

