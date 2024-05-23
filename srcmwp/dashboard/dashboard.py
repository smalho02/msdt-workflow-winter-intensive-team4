# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 26, 2012
@author: blubin
'''

import wx;
from wx import CallAfter;
from wax import DropDownBox;
from wax import Frame;
from wax import Application;
from .grandalfCanvas import GrandalfCanvas;
from workflow.workflow import Workflow;
from workflow.flowData import Status;
from workflow.flowData import FlowDataReference;

from workflow.result import Result;
from workflow.task import Task;
from workflow.util import enum;
import sys;
from dashboard.grandalfCanvas import NodeProperties;
from grandalf.graphs import Vertex;
from grandalf.graphs import Edge;
from grandalf.graphs import Graph;

State = enum("RED", "ORANGE", "YELLOW", "GREEN", "UNKNOWN")

class Node(object):
    def __init__(self, task=None, result=None):
        self.task=task;
        self.result=result;
        
    def get_state(self):
        # states we need to handle: (Task, Result)
        # None, NEW -> YELLOW
        # None, COMPLETE -> GREEN
        # NEW, None -> RED
        # NEW, NEW -> YELLOW
        # NEW, COMPLETE -> ORANGE
        # COMPLETE, None -> UNKNOWN
        # COMPLETE, NEW -> YELLOW
        # COMPLETE, COMPLETE-> GREEN
        # Otherwise: UNKNOWN 
        if self.task == None:
            if self.result == None:
                return State.UNKNOWN;
            elif self.result.status == Status.NEW:
                return State.YELLOW;
            elif self.result.status == Status.COMPLETE:
                return State.GREEN;
            else:
                return State.UNKNOWN;
        elif self.task.status == Status.NEW:
            if self.result == None:
                return State.RED;
            elif self.result.status == Status.NEW:
                return State.YELLOW;
            elif self.result.status == Status.COMPLETE:
                return State.ORANGE;
            else:
                return State.UNKNOWN;
        elif self.task.status == Status.COMPLETE:
            if self.result == None:
                return State.UNKNOWN;
            elif self.result.status == Status.NEW:
                return State.YELLOW;
            elif self.result.status == Status.COMPLETE:
                return State.GREEN;
            else:
                return State.UNKNOWN;
        else:
            return State.UNKNOWN;
        
    def get_parent_refs(self, cache):
        if self.task == None:
            return [];
        ret = [];
        if self.task.parents != None:
            for resultref in self.task.parents:
                result = cache.get_data(resultref);
                if result != None:
                    if result.parents == None or len(result.parents)==0:
                        ret.append(FlowDataReference.from_flow_data(result));
                    else:
                        ret.extend(result.parents);
        return ret;

class StepCache(object):
    '''
    Cache of a given step (or table)
    '''
    def __init__(self):
        self.rows= [];
        self.uids = {};

    def update(self, flowDatas):
        for row in flowDatas:
            if row.uid in self.uids:
                # Update existing entries:
                i = self.uids[row.uid];
                self.rows[i] = row;
            else:
                # Add new entries:
                self.rows.append(row);
                self.uids[row.uid] = len(self.rows)-1;

    def get(self, uid):
        if uid in self.uids:
            idx =  self.uids[uid];
            return self.rows[idx];
        return None;

class Cache(object):
    '''
    Cache of all the data about a given sequence number
    '''
    def __init__(self):
        self.taskcaches = {};
        self.resultcaches = {};

    def update(self, flowDatas):
        for d in flowDatas:
            if isinstance(d, Task):
                caches = self.taskcaches;
            elif isinstance(d, Result):
                caches = self.resultcaches;
            if d.stepname not in caches:
                caches[d.stepname] = StepCache();
            caches[d.stepname].update([d]);

    def get_data(self, ref, flowDataType=None):
        if flowDataType == None:
            flowDataType = ref.type;
        if not isinstance(flowDataType, str):
            flowDataType = flowDataType.__class__.__name__;
        if flowDataType == "Task":
            if ref.stepname in self.taskcaches:
                cache = self.taskcaches[ref.stepname];
            else:
                return None;
        elif flowDataType == "Result":
            if ref.stepname in self.resultcaches:
                cache = self.resultcaches[ref.stepname];
            else:
                return None;
        else:
            raise Exception("Unkown type: " + flowDataType);
        return cache.get(ref.uid);
    
    def get_summary_ref(self, d):
        if isinstance(d, Task):
            return FlowDataReference.from_flow_data(d);
        elif isinstance(d, Result):
            if d.parents == None or len(d.parents) == 0:
                return FlowDataReference.from_flow_data(d);
            elif len(d.parents) > 1:
                raise Exception("Results should only have one parent: " + d);
            return d.parents[0];
        else:
            raise Exception("Unknown type: " + d);

    def get_nodes(self):
        ret = {};
        for cache in self.taskcaches.values():
            for row in cache.rows:
                ref = self.get_summary_ref(row);
                if ref not in ret:
                    ret[ref] = Node(task=row);
                else:
                    ret[ref].task = row;
        for cache in self.resultcaches.values():
            for row in cache.rows:
                ref = self.get_summary_ref(row);
                if ref not in ret:
                    ret[ref] = Node(result=row);
                else:
                    ret[ref].result = row;
        return ret;
        
class SequenceChoice(DropDownBox):
    def __init__(self, parent, choices=[], size=None, **kwargs):
        super(SequenceChoice, self).__init__(parent, choices, size, **kwargs);
        
    def OnSelect(self, evt):
        self.Parent.set_active_sequence(self.get_selected_sequence());
        
    def get_selected_sequence(self):
        return int(self.GetStringSelection());    
        
class DashboardFrame(Frame):
    
    def __init__(self, workflow):
        Frame.__init__(self, title="Dashboard: " + workflow.flowname, direction="V");
        self.workflow = workflow;
        self.caches = {}; #Indexed by sequence number.
        self.active_sequence=0;
        self.workflow.register_all_table_listener(self.listener);
        #self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def Body(self):
        self.seqchoice = SequenceChoice(self);
        self.AddComponent(self.seqchoice, align="c");
        self.canvas = GrandalfCanvas(self)
        self.canvas.SetSize((800,600));
        self.AddComponent(self.canvas, expand="b");
        self.Pack();

    def listener(self, rows):
        redraw = False;
        seqs = set();
        for row in rows:
            sequence = row.sequence;
            if sequence == self.active_sequence:
                redraw = True;
            if sequence not in self.caches:
                self.caches[sequence] = Cache();
            self.caches[sequence].update([row]);
            seqs.add(str(row.sequence));
        CallAfter(self.update_seqs, seqs);
        if self.active_sequence == 0 and len(seqs) > 0:
            CallAfter(self.default_selection);
        if redraw:
            self.update();

    def update_seqs(self, seqs):
        for seq in sorted(seqs):
            if self.seqchoice.FindString(seq) == wx.NOT_FOUND:
                self.seqchoice.Append(seq);
            
    def default_selection(self):
        self.seqchoice.SetSelection(0);
        self.set_active_sequence(self.seqchoice.get_selected_sequence())
    
    def set_active_sequence(self, sequence):
        self.active_sequence = sequence;
        self.update();
    
    def update(self):
        (G, props) = self.get_graph();
        CallAfter(self.canvas.set_graph, G, props);

    def get_graph(self, sequence=None):
        if sequence==None:
            sequence = self.active_sequence;
        cache = self.caches[sequence];
        nodemap = cache.get_nodes();
        forward = list(nodemap.keys()); # num -> ref
        backward = dict([(v,k) for (k,v) in enumerate(forward)]); # ref -> num
        V = [Vertex(ref) for ref in forward];
        E = []
        for ref, node in nodemap.items():
            v = V[backward[ref]];
            for pref in node.get_parent_refs(cache):
                pv = V[backward[pref]];
                edge = Edge(v,pv);
                E.append(edge);
        G = Graph(V,E);
        props = {ref : NodeProperties(name=self.get_name(ref), color=self.state_to_color(nodemap[ref].get_state())) for ref in forward};
        return G, props;
    
    def state_to_color(self, state):
        if state == State.RED:
            return (200, 150, 150);
        elif state == State.ORANGE:
            return (240, 200, 100);
        elif state == State.YELLOW:
            return (240, 240, 180);
        elif state == State.GREEN:
            return (150, 200, 150);
        else:
            return (200, 200, 200);

    def get_name(self, ref):
        return ref.rolename + ":" + ref.stepname + "(" + str(ref.uid) +")";

    def OnClose(self, event):
        print('Closing!')
        self.workflow.terminate();
        print('DB Thread not terminated for now...')
        event.Skip();

class DashboardApplication(Application):
    def __init__(self, workflow):
        Application.__init__(self, DashboardFrame, workflow);
    
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Expected one argument, the name of the workflow");
        exit(1);
    print("Creating dashboard on: " + sys.argv[1]);
    workflow = Workflow(sys.argv[1]);
    app = DashboardApplication(DashboardFrame, workflow);
    app.MainLoop()
