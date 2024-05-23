# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

from wax import Application;
from .roleFrame import RoleFrame;
from workflow.workflow import Workflow;
from workflow.result import Result;
from workflow.flowData import Status;
from workflow.util import convert_rolename_to_db;
from workflow.util import convert_stepname_to_db;

class RoleApplication(Application):
    '''
    Base class for a given Role's UI
    '''

    def __init__(self, flowname, rolename):
        title = flowname + ": " + rolename;
        super(RoleApplication, self).__init__(RoleFrame, title=title);
        self.flowname = flowname;
        rolename = convert_rolename_to_db(rolename);
        self.rolename = rolename;
        self.mainframe.set_flow_name(flowname);
        self.mainframe.set_role_name(rolename);
        self.workflow = Workflow(flowname);
        self.mainframe.set_workflow(self.workflow);

    def register_source_step(self, stepname, form_creator, form_handler=None):
        stepname = convert_stepname_to_db(stepname);
        if form_handler == None:
            form_handler = self.default_form_handler;
        self.mainframe.register_source_step(stepname, form_creator, form_handler);

    def register_sink_step(self, stepname, form_creator, form_handler=None, name_fields=["sequence"]):
        stepname = convert_stepname_to_db(stepname);
        if form_handler == None:
            form_handler = self.default_sink_form_handler;
        self.mainframe.register_transition_step(stepname, form_creator, form_handler, name_fields);
            
    def register_transition_step(self, stepname, form_creator, form_handler=None, name_fields=["sequence"]):
        stepname = convert_stepname_to_db(stepname);
        if form_handler == None:
            form_handler = self.default_form_handler;
        self.mainframe.register_transition_step(stepname, form_creator, form_handler, name_fields);

    def default_form_handler(self, stepname, data, task):
        if task == None:
            result = Result(self.flowname, self.rolename, stepname, data);
        else:
            result = Result.construct_from_task(task, self.rolename, stepname, data);
        self.workflow.add(result);
        if task != None:
            self.workflow.update_status(task, Status.COMPLETE);

    def default_sink_form_handler(self, stepname, data, task):
        if task == None:
            result = Result(self.flowname, self.rolename, stepname, data, status=Status.COMPLETE);
        else:
            result = Result.construct_from_task(task, self.rolename, stepname, data, status=Status.COMPLETE);
        self.workflow.add(result);
        if task != None:
            self.workflow.update_status(task, Status.COMPLETE);
