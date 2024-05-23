# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

import sys
from xmlrpc.client import ServerProxy, Binary
import traceback;
#import cPickle as pickle
import pickle

from .flowData import Status, FlowDataReference;
from .task import Task
from .result import Result
from .joinedListener import JoinedListener
from .allTableListener import AllTableListener
from .SqliteDBUtils import TableReference, get_serverparams
from socket import error as socket_error

class SqliteDBClient(object):
    '''
    Manages storing the workflow data in the database.
    This is a db client that sits in every process.
    Communication is by XMLRPC
    '''
    
    ''' How many poll cycles to do before checking for all tables.'''
    ALL_TABLE_POLL_CYCLES = 1

    def __init__(self, flowname):
        """ flowname is the database file backing this flow """
        self.flowname = flowname
        serverparams = get_serverparams()
        self.tables = {} # TableReference -> _TableView
        self.all_table_listeners = []
        self.poll_count = 0        
        self.rpcclient = self._create_client(serverparams)
        
# PUBLIC
    
    def connect(self):
        ''' Actually connect to the database '''
        sys.stdout.write("Connecting to server... ")
        self.rpcclient.ensure_database_exists(self.flowname)
        print("done.")
    
    def add(self, flowData):
        table = self._get_table_flowdata(flowData)
        table.add_row(flowData)
        
    def update_status(self, flowData, status):
        table = self._get_table_flowdata(flowData)
        table.update_row(flowData.uid, "status", Status.reverse_mapping[status])

    def register_result_listener(self, rolename, stepname, listener, status=None):
        self.register_listener(rolename, stepname, Result, listener, status)

    def register_task_listener(self, rolename, stepname, listener, status=None):
        self.register_listener(rolename, stepname, Task, listener, status)

    def register_listener(self, rolename, stepname, flowDataCls, listener, status=None):
        tableref = TableReference(rolename, stepname, flowDataCls)
        table = self._get_table(tableref)
        table.register(listener, status)
        
    def register_joined_listener(self, listenlist, predicate, listener):
        '''
        Listen to one or more result tables, and fires when predicate says so.  
        Note: bins by 'sequence' field you only get results associated with the same sequence number 
        Arguments:
        listenlist: a list of tuples, each of the form (rolename, stepname, flowDataCls, status) to listen to.  FlowDataCls is Task or Result, If omitted, status defaults to Status.NEW
        predicate: a function, that takes a set of results obtained so far.  return True iff the set is complete and the event should fire.
        listener: the function to fire.  it takes a list of the results.
        '''
        JoinedListener(self, listenlist, predicate, listener)
        
    def register_all_table_listener(self, listener, status=None):
        ''' register a listener on all the tables. '''
        self.all_table_listeners.append(AllTableListener(self, listener, status))

# Private

    def _create_client(self, serverparams):
        ''' Connect to the server. '''
        # We create a wrapper that is a proxy to the proxy.  We need to do this because
        # XMLRPC which we use does not support user-defined classes, so we need to do our own
        # Marshalling via Pickle.
        class ProxyWrapper(object):
            ''' A wrapper for the proxy that handles pickling.  By default just dispatches
                to the proxy.  But if you need to pickle, define a function explicitly here.
            '''
            def __init__(self, serverparams):
                # On some machines resolving localhost takes a long time:
                if serverparams.address == "localhost":
                    address = "127.0.0.1"
                else:
                    address = serverparams.address
                url = "http://"+address + ":" + str(serverparams.port)
                self.xmlproxy = ServerProxy(url, allow_none=True) # The xmlrpc client itself
            
            def __getattr__(self, attr):
                # This only gets called for attributes that haven't been defined.
                # If this happens, try to get the attribute from the xmlproxy instead.
                if hasattr(self.xmlproxy, attr):
                    return getattr(self.xmlproxy, attr)
                else:
                    # If its not defined either in this class, or in the proxy class, then its an error
                    raise AttributeError(attr)
                
            @staticmethod
            def to_bin(obj):
                # Handle python3 issue where dictionary key views are not pickleable
                from _collections_abc import dict_keys
                if isinstance(obj, dict_keys):
                    obj = [x for x in obj] 
                return Binary(pickle.dumps(obj))

            @staticmethod
            def from_bin(bin):
                return pickle.loads(bin.data)
                
            # Define any methods that need marshalling/unmarshelling here.
            
            def ensure_table_exists(self, flowname, tableref):
                return self.xmlproxy.ensure_table_exists(flowname, self.to_bin(tableref))
            
            def get_records(self, flowname, tableref):
                ret = self.xmlproxy.get_records(flowname, self.to_bin(tableref))
                return self.from_bin(ret)

            def get_table_references(self, flowname):
                ret = self.xmlproxy.get_table_references(flowname)
                return self.from_bin(ret)
            
            def ensure_all_fields_present(self, flowname, tableref, fieldnames):
                ret = self.xmlproxy.ensure_all_fields_present(flowname, self.to_bin(tableref), self.to_bin(fieldnames))
                return self.from_bin(ret)

            def add_table_row(self, flowname, flowData):
                return self.xmlproxy.add_table_row(flowname, self.to_bin(flowData))
            
            def update_table_row(self, flowname, tableref, uid, column, value):
                self.xmlproxy.update_table_row(flowname, self.to_bin(tableref), uid, column, value)
                
        return ProxyWrapper(serverparams)

    def _get_table_flowdata(self, flowData):
        ''' Get the _Table that would store the given object'''
        if flowData.flowname != self.flowname:
            raise Exception("Mismatched flow names: " + flowData.flowname)
        tableref = TableReference(flowData.rolename, flowData.stepname, flowData.__class__)
        table = self._get_table(tableref)
        table.check_columns(flowData.data.keys())
        return table

    def _get_table(self, tableref):
        ''' Get the table for the given reference '''
        if tableref not in self.tables:
            self.tables[tableref] = _TableView(self.rpcclient, self.flowname, tableref)
        table = self.tables[tableref]
        return table
        
    def _get_table_references(self):
        ''' Get the table references -- all of them in the DB, not just the cache. '''
        return self.rpcclient.get_table_references(self.flowname)
    
    def poll(self):
        ''' Call this in the worker thread periodically.  All callbacks will occur within this context.'''
        for table in self.tables.values():
            try:
                table.poll();
            except socket_error as serr:
                raise serr
            except Exception as e:
                print("Exception updating table: " + str(type(e)) + ": " + str(e));
                print(traceback.format_exc());
        # Only do this every 5 polls:
        if self.poll_count%SqliteDBClient.ALL_TABLE_POLL_CYCLES==0:
            tablerefs = self._get_table_references();
            for listener in self.all_table_listeners:
                try:
                    listener.poll(tablerefs);
                except socket_error as serr:
                    raise serr
                except Exception as e:
                    print("Exception updating all table listener: " + str(type(e)) + ": " + str(e));
                    print(traceback.format_exc());
        self.poll_count = self.poll_count+1;
        
class _TableView(object):
    """
    A View of a particular table in the database.
    - Caches the content locally
    - Maintains the ability to fire listeners against changes in this data
    
    """        
    def __init__(self, rpcclient, flowname, tableref):
        self.rpcclient = rpcclient
        self.flowname = flowname
        self.tableref = tableref
        self.listeners = [] # Tuples, (Status, Listener)
        self.rows = {} # uid -> FlowData subclass
        self.fields = set() # Cached to reduce calls to ensure_all_fields_present
        self.ensure_exists()
    
    def ensure_exists(self):
        """ Ensure the table exists in the DB """
        sys.stdout.write('Checking for table ' + str(self.tableref) +"... ")
        self.rpcclient.ensure_table_exists(self.flowname, self.tableref)
        print("done.")
    
    def check_columns(self, fieldnames):
        """ Check that the columns are all present.  Can cache names so this is fast."""
        if len(set(fieldnames).difference(self.fields)) > 0: # Does it match the cache?
            # Cache miss, so update the db:
            sys.stdout.write("Table " + str(self.tableref) + " has new fields... ")
            newfields = self.rpcclient.ensure_all_fields_present(self.flowname, self.tableref, fieldnames)
            print(", ".join(set(newfields).difference(self.fields)))
            self.fields.update(newfields)
    
    def register(self, listener, status=None):
        """ Register a listener for the given status.  None means get all events"""
        self.listeners.append((status,listener))
        # Fire any existing rows against the listener:
        updated = self._restrict(self.rows.values(), status)
        if len(updated) > 0:
            listener(updated);
    
    def add_row(self, flowData):
        """ Add the given row to the table."""
        sys.stdout.write("Adding to " + str(self.tableref) + ": " + str(flowData) +"...")
        self.rpcclient.add_table_row(self.flowname, flowData)
        print("done.")
    
    def update_row(self, uid, column, value):
        """ Update a given field in a given row."""
        sys.stdout.write("Updating " + str(self.tableref) + "[" + str(uid) + "] " + column + "<-"+ str(value)+"...")
        self.rpcclient.update_table_row(self.flowname, self.tableref, uid, column, value)
        print("done.")
        
    def poll(self):
        """ Update the table cache """
        results = self.rpcclient.get_records(self.flowname, self.tableref)
        if results == None or len(results) == 0:
            return
        updated = [];
        for dbData in results:
            cacheData = None;
            if dbData.uid in self.rows:
                cacheData = self.rows[dbData.uid];
            if not dbData == cacheData:
                self.rows[dbData.uid] = dbData;
                updated.append(dbData);
        if len(updated) > 0:
            self._fire_updates(updated);
            
    def _fire_updates(self, updated):
        for status, listener in self.listeners:
            upd = self._restrict(updated, status);
            if len(upd) > 0:
                listener(upd);

    @staticmethod                
    def _restrict(rows, status=None):
        ''' Return a list of only those rows with the given status'''
        if status == None:
            return rows
        else:
            ret = [];
            for r in rows:
                if r.status == status:
                    ret.append(r);
            return ret

