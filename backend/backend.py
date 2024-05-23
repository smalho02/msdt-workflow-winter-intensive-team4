# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Defines the base class for the backend processor needed for any MWP application.
'''

# TODO:  review documentation for backend.py

from workflow.workflow import Workflow;
from workflow.flowData import Status;
from workflow.SqliteDBServer import SqliteDBServer
from dashboard.dashboard import DashboardApplication;

class Backend(object):
    '''
    Base class for backend processor.
    '''

    def __init__(self, flowname, dashboard=True, server=True):
        '''
        initializes the backend processor.
        
        The actual backend just needs to call this method and pass in the
        parameters.
        
        flowname is the name of this workflow.  It is 
        used to name the spreadsheet where this workflow's data
        will be stored and is also used when initializing front end
        applications so as to identify all the tasks
        associated with this workflow.
        
        dashboard specifies whether the dashboard should be displayed
        when this backend runs.  dashboard is set to TRUE by default.
        '''
        if server:
            self.server = SqliteDBServer()
        self.flowname = flowname;
        self.workflow = Workflow(flowname);
        self.workflow.queue.put(lambda: self.wire());
        if dashboard:
            self.dashboard = DashboardApplication(self.workflow);
            self.dashboard.MainLoop()
 
    def wire(self):
        '''
        The actual backend needs to define a wire method which should 
        register all tasks to be monitored as part of this workflow.
        Tasks are registered using one of the methods which follow.
        '''
        pass;

    def register_result_listener(self, rolename, stepname, listener, status = Status.NEW):
        self.workflow.register_result_listener(rolename, stepname, listener, status);

    def register_joined_listener(self, listenlist, predicate, listener):
        '''
        Listen to one or more result tables, and fires when predicate says so.  
        Note: bins by 'sequence' field; you only get results associated with the same sequence number 
        Arguments:
        listenlist: a list of tuples, each of the form (rolename, stepname, status) to listen to.  If omitted, status defaults to Status.NEW
        predicate: a function, that takes a set of results obtained so far.  return True iff the set is complete and the event should fire.
        listener: the function to fire.  it takes a list of the results.
        '''
        self.workflow.register_joined_listener(listenlist, predicate, listener);
