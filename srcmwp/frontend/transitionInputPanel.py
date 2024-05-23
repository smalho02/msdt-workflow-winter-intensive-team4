# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 16, 2012
@author: blubin
'''

from wx import CallAfter;
from wax import Panel;
from wax import ListBox;
from .inputPanel import InputPanel;
from workflow.flowData import Status;
from workflow.util import convert_fieldname_to_db;

class TransitionInputPanel(InputPanel, Panel):

    def __init__(self, parent, workflow, rolename, stepname, form_creator, form_handler, name_fields=["sequence"]):
        Panel.__init__(self, parent, direction="horizontal");
        InputPanel.__init__(self, stepname, form_creator, form_handler)
        self.workflow = workflow;
        self.rolename = rolename;
        self.name_fields = name_fields;
        self.tasks = [];
        self.uid = {};
        self.temp_ignore = {};
        self.AddComponent(self.create_task_control(), expand="v");
        self.Pack();

    def create_task_control(self):
        self.task_box = ListBox(self, size=(175, 1), selection='single');
        self.task_box.OnClick = self.task_clicked;
        self.workflow.register_task_listener(self.rolename, self.stepname, lambda u : CallAfter(self.task_list_updater, u));
        return self.task_box;

    def task_list_updater(self, tasks):
        selectionIdx = self.task_box.GetSelection();
        if selectionIdx >= 0:
            selectionID = self.tasks[selectionIdx].uid;
        for task in tasks:
            if task.status == Status.NEW:            
                if task.uid in self.temp_ignore:
                    continue;
                # Add new entries:
                if task.uid in self.uid:
                    i = self.uid[task.uid];
                    self.tasks[i] = task;
                else:
                    self.tasks.append(task);
                    self.uid[task.uid] = len(self.tasks)-1;
            elif task.status == Status.COMPLETE:
                if task.uid in self.temp_ignore:
                    del self.temp_ignore[task.uid];
                # Remove complete entries:
                if task.uid in self.uid:
                    i = self.uid[task.uid];
                    del self.tasks[i];
                    del self.uid[task.uid];
                    self.decrement_above(i);
                
        self.task_box.SetItems(self.build_item_list());
        if selectionIdx >= 0:
            if selectionID in self.uid:
                newSelectionIdx = self.uid[selectionID];
                self.task_box.SetSelection(newSelectionIdx);
            else:
                print("Task backing active form, removed");
                self.task_box.SetSelection(-1);
                self.remove_form();
                
    def decrement_above(self, idx):
        for uid in self.uid:
            if self.uid[uid] >= idx:
                self.uid[uid] = self.uid[uid]-1;
        

    def build_item_list(self):
        ret = [(self.get_field(t), t) for t in self.tasks];
        return ret;

    def get_field(self, flowObj):
        label ="";
        for fn in self.name_fields:
            if fn== "sequence":
                s = flowObj.sequence;
            elif fn == "status":
                s = Status.reverse_mapping[flowObj.status];
            else:
                fn = convert_fieldname_to_db(fn);
                s = flowObj.data[fn];
            label += str(s) + " ";
        return label;
    
    def task_clicked(self, event):
        task = self.tasks[event.GetSelection()];
        if task == self.current_task:
            return;
        if self.current_task:
            self.remove_form();
        self.form_panel = self.create_form_panel(task);
        self.AddComponent(self.form_panel, expand="b");
        CallAfter(self.Layout);
        CallAfter(self.Repack);

    def form_ok(self, event):
        task = self.form.task;
        InputPanel.form_ok(self, event);
        self.task_box.SetSelection(-1);
        # Modify the existing task to complete, and update it locally.  The listener will do this too, but this prevents a lag:
        task.status = Status.COMPLETE;
        self.task_list_updater([task]);
        #Ignore updates on this task, until it goes to complete.
        self.temp_ignore[task.uid]=None;
        
    def form_cancel(self, event):
        self.task_box.SetSelection(-1);
        InputPanel.form_cancel(self, event);

    def remove_form(self):
        if hasattr(self, "form_panel"):
            InputPanel.remove_form(self);
            CallAfter(self.form_panel.Destroy);  # need to delay this call to avoid a 2.9 crash
            del self.form_panel;
            self.Layout();
            self.Repack();
