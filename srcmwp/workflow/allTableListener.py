# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 28, 2012
@author: blubin
'''

class AllTableListener(object):
    '''
    Class that ensures the supplied listener is always registered on all tables.
    '''

    def __init__(self, db, listener, status):
        self.db = db;
        self.listener = listener;
        self.status = status;
        self.tablerefs = set();
        
    def poll(self, currefs):
        newrefs = currefs.difference(self.tablerefs);
        for ref in newrefs:
            self.db.register_listener(ref.rolename, ref.stepname, ref.flowDataCls, self.listener, self.status);
        self.tablerefs.update(newrefs);