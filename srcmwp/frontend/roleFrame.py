# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

from wax import Frame;
from wax import NoteBook;
from wax import Splitter;
from .outputPanel import OutputPanel;
from .sourceInputPanel import SourceInputPanel;
from .transitionInputPanel import TransitionInputPanel;

class RoleFrame(Frame):

    def __init__(self, parent=None, title="", direction="H", size=None, **kwargs):
        Frame.__init__(self, parent=parent, title=title, direction=direction, size=size, **kwargs)

    def set_flow_name(self, flowname):
        self.flowname = flowname;
        
    def set_role_name(self, rolename):
        self.rolename = rolename;
        
    def set_workflow(self, workflow):
        self.workflow = workflow;

    def Body(self):
        self.nb = NoteBook(self);
        self.nb.Size = (800, 600);
        self.AddComponent(self.nb, expand='both');
        self.Pack();
        
    def OnClose(self, event):
        self.workflow.terminate();
        event.Skip();

    def register_source_step(self, stepname, form_creator, form_handler):
        sourceTab = Splitter(self.nb, size=(800,600), );
        inputPanel = SourceInputPanel(sourceTab, stepname, form_creator, form_handler);
        self.complete_step_registration(sourceTab, inputPanel, stepname);

    def register_transition_step(self, stepname, form_creator, form_handler, name_fields):
        sourceTab = Splitter(self.nb, size=(800,600), );
        inputPanel = TransitionInputPanel(sourceTab, self.workflow, self.rolename, stepname, form_creator, form_handler, name_fields);
        self.complete_step_registration(sourceTab, inputPanel, stepname);
        
    def complete_step_registration(self, sourceTab, inputPanel, stepname):
        outputPanel = OutputPanel(sourceTab, self.workflow, self.rolename, stepname);
        sourceTab.Split(inputPanel, outputPanel, direction="horizontal", sashposition=300);
        self.nb.AddPage(sourceTab, stepname);
