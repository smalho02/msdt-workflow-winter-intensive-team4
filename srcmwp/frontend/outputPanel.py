# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 16, 2012
@author: blubin
'''

import wx
from wax import Grid;
from wx import CallAfter;
from wx.grid import GridTableBase; 
from wx.grid import GRID_VALUE_STRING; 
from workflow.flowData import Status;
from workflow.flowData import FlowDataReference;

class OutputPanel(Grid):

    def __init__(self, parent, workflow, rolename, stepname):
        Grid.__init__(self, parent, numrows=0, numcolumns=0);
        self.EnableEditing(False);
        self.grid_table = GridTable();
        self.SetTable(self.grid_table);
        workflow.register_result_listener(rolename, stepname, lambda u : CallAfter(self.listener, u));
        #workflow.register_result_listener(rolename, stepname, self.listener);

    def listener(self, updates):
        self.grid_table.update(updates);
        self.SetTable(self.grid_table);
        self.AutoSizeColumns();
        
class GridTable(GridTableBase):
    
    def __init__(self):
        GridTableBase.__init__(self);
        self.rows = [];
        self.cols = None;
        self.uid = {};
            
    def update(self, updates):
        for u in updates:
            if u.uid in self.uid:
                r = self.uid[u.uid];
                self.rows[r] = u;
            else:
                self.rows.append(u);
                self.uid[u.uid] = len(self.rows)-1;
    
    def GetNumberRows(self):
        return max(1, len(self.rows));

    def GetNumberCols(self):
        if len(self.rows) == 0:
            return 1;
        else:
            return len(self.rows[0].data.keys()) + 3;

    def IsEmptyCell(self, row, col):
        return False

    def GetTypeName(self, row, col):
        return GRID_VALUE_STRING;

    def GetValue(self, row, col):
        if len(self.rows) == 0:
            return "No Data Yet";
        thecol = self.get_column(col);
        therow = self.rows[row];
        if thecol == 'status':
            return Status.reverse_mapping[therow.status];
        if thecol == 'sequence':
            return therow.sequence;
        if thecol == 'parents':
            if therow.parents == None:
                return "";
            else:
                return ','.join([FlowDataReference.to_string(k) for k in therow.parents]);
        v = therow.data[thecol];
        if v == None:
            return "";
        return v;

    def get_column(self, col):
        if self.cols == None:
            self.cols = [k for k in self.rows[0].data.keys()];
        if col - len(self.cols) == 0:
            return 'sequence';
        if col - len(self.cols) == 1:
            return 'parents';        
        if col - len(self.cols) == 2:
            return 'status';        
        return self.cols[col];

    def GetColLabelValue(self, col):
        if self.cols == None:
            return "";
        else:
            return self.get_column(col);

    def SetValue(self, row, col, value):
        pass;