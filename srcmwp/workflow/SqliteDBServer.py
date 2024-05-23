# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

import sys
from threading import Thread
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import sqlite3
from contextlib import closing
from collections import OrderedDict;
from xmlrpc.client import Binary
#import cPickle as pickle
import pickle
import traceback

from .flowData import Status, FlowDataReference;
from .task import Task
from .result import Result
from .SqliteDBUtils import TableReference, get_serverparams

class SqliteDBServer(object):
    '''
    Presently a pretty thin wrapper around SQLite.  
    
    All public methods of this class are made available over the network.
    '''
    
    ''' Should loggin happen server side '''
    verbose = False
    
    def __init__(self):
        self.db = {} # Flowname to DB Connection
        serverparams = get_serverparams(alwayslocalhost=True)
        self._log("Starting Server... ")
        self.server = self._create_server(serverparams)
        # Create a thread to handle the requests
        self.thread = _ServerThread(self.server.xmlserver)
        self.thread.start()
        self._logln("done.")
        
# Public
    
    def stop_server(self, join=False):
        ''' Stop the server.  
            if join==True, then we join against the server thread to block until shutdown
        '''
        self._log("Stopping server... ")
        self._log("Shutdown isn't automatic for now...")
        #self.server.shutdown()
        #for db in self.db.values():
            # Note: anything happening right now will be lost... (No commit)
        #   db.close()        
        if join:
            self.thread.join()
        self._logln("done.")

    def ensure_database_exists(self, flowname):
        ''' Make sure a database for the given flowname exists. '''
        if not flowname in self.db:
            self.db[flowname] = sqlite3.connect(flowname+".db") 
            self.db[flowname].row_factory = sqlite3.Row # Let us look up row entries by name
            self.db[flowname].text_factory = str #Make strings not unicode
            print("Opened DB file: " + flowname + ".db")
    
    def get_table_references(self, flowname):
        ''' Get all the table references in the DB. '''
        self.ensure_database_exists(flowname)
        self._log("Getting all tables... ")
        ret = set();
        with closing(self.db[flowname].cursor()) as c:
            # We can get all the table names with following SQL:
            c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
            for r in c.fetchall():
                ref = self._get_tableref(r['name']);
                if ref != None:
                    ret.add(ref);
        self._logln("done.")
        return ret;
    
    def ensure_table_exists(self, flowname, tableref):
        """ Ensure the table exists in the DB """
        self.ensure_database_exists(flowname)
        self._log('Ensuring existence of ' + str(tableref) + "... ")
        with closing(self.db[flowname].cursor()) as c:
            tablename = self._get_tablename(tableref)
            # Can't do tablename with parameter...
            c.execute("CREATE TABLE IF NOT EXISTS "+tablename+"(sequence INT, status INT, parents TEXT);") 
            self.db[flowname].commit()
        self._logln("done.")
                    
    def ensure_all_fields_present(self, flowname, tableref, fieldnames):
        """ Update the table so that it definitely includes all the columns provided.
            Returns: the current set of field (column) names.
        """
        self.ensure_database_exists(flowname)
        self._log('Ensuring existence of columns in' + str(tableref) + "... ")
        fieldnames = set(fieldnames)
        with closing(self.db[flowname].cursor()) as c:
            # First get the existing names
            tablename = self._get_tablename(tableref)
            c.execute("PRAGMA table_info(" + tablename + ");")
            columns = set([r['name'] for r in c.fetchall()])
            # Now any names not already present need to be added:
            toadd =  fieldnames.difference(columns)
            for field in toadd:
                c.execute("ALTER TABLE " + tablename + " ADD COLUMN " + field + ";")
            if len(toadd) > 0:
                self._logln("Added columns: " + ", ".join(toadd))
            else:
                self._logln("done.")
        return columns.union(toadd)

    def add_table_row(self, flowname, flowData):
        """ Add the given row to the db """
        self.ensure_database_exists(flowname)
        tableref = self._get_tableref_for_data(flowData)
        tablename = self._get_tablename(tableref)
        if flowData.uid != None:
            sys.stderr.write("Unepected UID: " + str(flowData.uid) + "\n")
        self._log('Adding to ' + str(tableref) + ": " +  str(flowData.sequence) + "." + str(flowData.uid) + "... ");
        # First build up a dictionary of the values:
        row = OrderedDict(flowData.data);
        row['status'] = Status.reverse_mapping[flowData.status];
        if flowData.sequence == None:
            flowData.sequence = self._get_new_sequence(flowname, tableref);
        row['sequence'] = flowData.sequence;
        if flowData.parents == None:
            row['parents'] = "";
        else:
            row['parents'] = ",".join([FlowDataReference.to_string(p) for p in flowData.parents]);
        # Now run the insert:
        with closing(self.db[flowname].cursor()) as c:
            # Just build with some strings to make it easier, if not as secure...
            columns = ",".join(row.keys())
            slots = ",".join(["?"]*len(row.keys())) # Make comma separated '?'
            c.execute("INSERT INTO " + tablename + " (" + columns + ") VALUES (" + slots + ");", [v for v in row.values()])
            self.db[flowname].commit()
        self._logln("done.");

    def update_table_row(self, flowname, tableref, uid, column, value):
        """ Update the given row/column in the DB """
        self.ensure_database_exists(flowname)
        self._log('Updating ' + str(tableref) + " (" +  str(uid) + ") " + column + "<-" + str(value) + "... ")
        tablename = self._get_tablename(tableref)
        with closing(self.db[flowname].cursor()) as c:
            c.execute("UPDATE " +tablename +" SET " + column +" = ? where rowid = ?;",(value, uid))
            self.db[flowname].commit()
        self._logln("done.")

    def get_records(self, flowname, tableref):
        """ Get the records for the table """
        self.ensure_database_exists(flowname)
        self._log('Getting rows for ' + str(tableref) + "... ")
        tablename = self._get_tablename(tableref)
        ret = []
        with closing(self.db[flowname].cursor()) as c:
            c.execute("select rowid, * from " + tablename + ";")
            for r in c.fetchall():
                data = self.create_flow_data(flowname, tableref, r)
                if data != None:
                    ret.append(data)
        self._logln("done.")
        return ret

# Private

    def _log(self, msg):
        if SqliteDBServer.verbose:
            sys.stdout.write(msg)

    def _logln(self, msg):
        self._log(msg+"\n")

    def _get_new_sequence(self, flowname, tableref):
        self._log('Obtain new sequence for ' + str(tableref) + "... ")
        with closing(self.db[flowname].cursor()) as c:
            tablename = self._get_tablename(tableref)
            c.execute("SELECT sequence FROM " + tablename + " ORDER BY sequence DESC LIMIT 1;")
            seq = c.fetchone()
            if seq == None:
                nseq = 1
            else:
                nseq = seq[0] + 1
        self._logln("done.")
        return nseq

    def create_flow_data(self, flowname, tableref, result):
        #Hack to attempt to prevent race conditions:
        if 'status' not in result.keys():
            return None;        
        status = result['status'];
        status = Status.__dict__[status]; #Convert to numeric
        sequence = (int)(result['sequence']);
        if 'parents' in result.keys() and result['parents'] != "" and result['parents']!=None:
            parents = result['parents'].split(",");
        else:
            parents = None;
        data = OrderedDict();
        for field in result.keys():
            if field != 'status' and field != 'sequence' and field != 'parents' and field != 'rowid':
                data[field] = result[field];
                if isinstance(data[field], str):
                    data[field] = data[field]
        if result['rowid'] == None:
            uid = None
        else:
            uid = int(result['rowid']);
        flowData = tableref.flowDataCls(flowname, tableref.rolename, tableref.stepname, data, sequence, status, uid, parents);
        return flowData

    def _get_tableref_for_data(self, flowData):
        return TableReference(rolename=flowData.rolename, stepname=flowData.stepname, flowDataCls=flowData.__class__);

    def _get_tablename(self, tableref):
        if tableref.flowDataCls == Task:
            tablename = "T_" + tableref.stepname + "_" + tableref.rolename;
        elif tableref.flowDataCls == Result:
            tablename = "R_" + tableref.stepname + "_" + tableref.rolename;
        else:
            raise Exception("Unknown flowData: " + str(tableref.flowDataCls));
        return tablename
    
    def _get_tableref(self, tablename):
        s = tablename.split("_");
        if s[0] == "R":
            flowDataCls = Result;
        elif s[0] == "T":
            flowDataCls = Task;
        else:
            return None;
        return TableReference(rolename=s[2], stepname=s[1], flowDataCls=flowDataCls);
    
    def _create_server(self, serverparams):
        # We create a wrapper that is a proxy to the server.  We need to do this because we use
        # XMLRPC which we use does not support user-defined classes, so we need to do our own
        # Marshalling via Pickle.

        # Note: self will be the instance to call the members of.
        class ServerWrapper(object):
            ''' A wrapper for the server that handles pickling.  By default just dispatches
                to the server.  But if you need to pickle, define a function explicitly here.
            '''
            def __init__(self, serverparams, instance):
                # On some machines resolving localhost takes a long time:
                if serverparams.address == "localhost":
                    address = "127.0.0.1"
                else:
                    address = serverparams.address
                self.xmlserver = SimpleXMLRPCServer((address, serverparams.port),\
                                                    _ExceptionThrowingXMLRPCRequestHandler,\
                                                    allow_none=True,\
                                                    logRequests=False)
                # All public methods of this class are registered
                self.xmlserver.register_instance(self) 
                self.proxiedinstance = instance
            
            def __getattr__(self, attr):
                # This only gets called for attributes that haven't been defined.
                # If this happens, try to get the attribute from the xmlproxy instead.
                if hasattr(self.proxiedinstance, attr):
                    return getattr(self.proxiedinstance, attr)
                else:
                    # If its not defined either in this class, or in the proxy class, then its an error
                    raise AttributeError(attr)
                
            @staticmethod
            def to_bin(obj):
                return Binary(pickle.dumps(obj))

            @staticmethod
            def from_bin(bin):
                return pickle.loads(bin.data)
        
            # Define any methods that need marshalling/unmarshelling here.
           
            def ensure_table_exists(self, flowname, BINtableref):
                self.proxiedinstance.ensure_table_exists(flowname, self.from_bin(BINtableref))

            def get_records(self, flowname, BINtableref):
                ret = self.proxiedinstance.get_records(flowname, self.from_bin(BINtableref))
                return self.to_bin(ret)
            
            def get_table_references(self, flowname):
                ret = self.proxiedinstance.get_table_references(flowname)
                return self.to_bin(ret)
            
            def ensure_all_fields_present(self, flowname, BINtableref, BINfieldnames):
                ret = self.proxiedinstance.ensure_all_fields_present(flowname, self.from_bin(BINtableref), self.from_bin(BINfieldnames))
                return self.to_bin(ret)

            def add_table_row(self, flowname, BINflowData):
                self.proxiedinstance.add_table_row(flowname, self.from_bin(BINflowData))

            def update_table_row(self, flowname, BINtableref, uid, column, value):
                self.proxiedinstance.update_table_row(flowname, self.from_bin(BINtableref), uid, column, value)
                
        return ServerWrapper(serverparams, self) #The SqliteDBServer will be the instance to delegate to

class _ExceptionThrowingXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):
    """ A XMLRPC Handler that raises appropriate exceptions. """
    def _dispatch(self, method, params):
        try: 
            func = getattr(self.server.instance, method)
            return func(*params)
        except:
            traceback.print_exc()
            raise    
         
class _ServerThread(Thread):
    ''' Super simple thread that will execute the server'''
    def __init__(self, server):
        Thread.__init__(self, name="DBServer")
        self.server = server
    def run(self):
        self.server.serve_forever() # Internal server loop that handles requests
        print("SqliteDBServer Thread Ended.")
        