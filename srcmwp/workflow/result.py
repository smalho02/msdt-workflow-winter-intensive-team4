# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

from .flowData import FlowData;
from .flowData import Status;
from collections import OrderedDict;

class Result(FlowData):
    '''
    Represents the completion of a task
    '''

    def __init__(self, flowname, rolename, stepname, data=OrderedDict(), sequence=None, status=Status.NEW, uid=None, parents=None):
        FlowData.__init__(self, flowname, rolename, stepname, data, sequence, status, uid, parents);
        
    @classmethod    
    def construct_from_task(cls, task, rolename, stepname, data=OrderedDict(), status=Status.NEW, uid=None, copy=True, parents=None):
        if parents == None:
            parents = task;
        instance = cls(task.flowname, rolename, stepname, data, task.sequence, status, uid, parents);
        if copy:
            # Put the existing data in first.
            temp = instance.data;
            instance.data = OrderedDict(task.data);
            instance.data.update(temp);
        return instance;