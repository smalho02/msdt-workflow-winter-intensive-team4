# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 16, 2012
@author: blubin
'''

from wax import Panel;
from wax import Button;
from .form import Form;

class InputPanel(object):
    '''
    Base class for InputPanels
    '''
    def __init__(self, stepname, form_creator, form_handler):
        self.stepname = stepname;
        self.form_creator = form_creator;
        self.form_handler = form_handler;
        self.form = None;
        self.current_task = None;
    
    def create_form_panel(self, task=None):
        self.current_task = task;
        panel = Panel(self, direction="vertical");
        self.form = Form(panel, self.stepname, self.form_creator, self.form_handler, task);
        panel.AddComponent(self.form, expand="b");
        panel.AddComponent(self.create_button_panel(panel), expand="h");        
        panel.Pack();
        return panel;
        
    def create_button_panel(self, parent):
        buttons = Panel(parent);
        ok = Button(buttons, "Ok", event = self.form_ok);
        cancel = Button(buttons, "Cancel", event = self.form_cancel);
        buttons.AddSpace(1, 1, expand='h')
        buttons.AddComponent(ok);
        buttons.AddComponent(cancel);
        buttons.AddSpace(1, 1, expand='h')
        buttons.Pack();
        return buttons;

    def form_ok(self, event):
        self.form.submit();
        self.remove_form();
        
    def form_cancel(self, event):
        self.remove_form();
        
    def remove_form(self):    
        self.form = None;
        self.current_task = None;
