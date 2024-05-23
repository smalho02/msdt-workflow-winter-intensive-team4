# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 13, 2012
@author: blubin
'''

#from googleDB import GoogleDB;
import sys, time
from threading import Thread;
from queue import Queue, Empty;
from .SqliteDBClient import SqliteDBClient
from socket import error as socket_error

class Workflow(object):
    """ Represents the workflow.  Handles threading, so the Database Operations occur in their own thread."""

    POLL_DELAY = .5

    def __init__(self, flowname):
        self.flowname = flowname;
        self.queue = Queue();
        self.go = True;
        self.db = None
        self.connected = False
        self.thread = Thread(target=self.work, name="Workflow");
        self.thread.start();
    
# PUBLIC:
    
    def add(self, flowData):
        self.queue.put(lambda: self.db.add(flowData));
                
    def update_status(self, flowData, status):
        self.queue.put(lambda: self.db.update_status(flowData, status));

    def register_result_listener(self, rolename, stepname, listener, status=None):
        ''' register a listener for results.  callback obtains an array of results. status restricts to a given status where None means all. '''
        self.queue.put(lambda: self.db.register_result_listener(rolename, stepname, listener, status));        

    def register_task_listener(self, rolename, stepname, listener, status=None):
        ''' register a listener for tasks.  callback obtains an array of results. status restricts to a given status where None means all. '''
        self.queue.put(lambda: self.db.register_task_listener(rolename, stepname, listener, status));        

    def register_joined_listener(self, listenlist, predicate, listener):
        '''
        Listen to one or more result tables, and fires when predicate says so.  
        Note: bins by 'sequence' field; you only get results associated with the same sequence number 
        Arguments:
        listenlist: a list of tuples, each of the form (rolename, stepname, flowDataCls, status) to listen to.  FlowDataCls is Task or Result, If omitted, status defaults to Status.NEW
        predicate: a function, that takes a set of results obtained so far.  return True iff the set is complete and the event should fire.
        listener: the function to fire.  it takes a list of the results.
        '''
        self.queue.put(lambda: self.db.register_joined_listener(listenlist, predicate, listener));        
        
    def register_all_table_listener(self, listener, status=None):
        ''' register a listener on all the tables. '''
        self.queue.put(lambda: self.db.register_all_table_listener(listener, status));
        
# PRIVATE:    

    #Make this class a Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Workflow, cls).__new__(cls)
        return cls._instance

    def work(self):
        while(self.go):
            if not self.connected:
                try:
                    self.init_db();
                except socket_error as serr:
                    sys.stderr.write('Cannot connect to backend: ' + str(serr) +"\n")
                    time.sleep(1)
                    continue
            try:
                call = self.queue.get_nowait()
                call();
                self.queue.task_done();
            except socket_error as serr:
                sys.stderr.write('Cannot connect to backend: ' + str(serr) +"\n")
                self.queue.task_done();
                self.queue.put(call) # This should be a pushback, but Queue doesn't support it
            except Empty:
                try:
                    self.poll();
                    time.sleep(Workflow.POLL_DELAY)
                except socket_error as serr:
                    sys.stderr.write('Cannot connect to backend: ' + str(serr) +"\n")
        print("Workflow Thread Ended.")

    def terminate(self):
        self.go = False;

    def init_db(self):
        if self.db == None:
            self.db = SqliteDBClient(self.flowname);
        self.db.connect()
        self.connected = True
        
    def poll(self):
        sys.stdout.write('.')
        self.db.poll(); 
