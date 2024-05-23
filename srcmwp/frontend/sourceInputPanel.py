# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 16, 2012
@author: blubin
'''

import wx
from wax import OverlayPanel;
from wax import Panel;
from wax import Button;
from .inputPanel import InputPanel;

class SourceInputPanel(InputPanel, OverlayPanel):

    def __init__(self, parent, stepname, form_creator, form_handler):
        OverlayPanel.__init__(self, parent);
        InputPanel.__init__(self, stepname, form_creator, form_handler)
        self.SetSize((800,600));
        self.AddComponent(self.create_new_form_button_panel());
        self.Select(0);
        self.Pack();

    def create_new_form_button_panel(self):
        newFormButtonPanel = Panel(self, direction="h");
        newFormButton = Button(newFormButtonPanel, "New " + self.stepname, event=self.new_form_button_handler);
        newFormButtonPanel.AddSpace(1, 1, expand="b");
        newFormButtonPanel.AddComponent(newFormButton);
        newFormButtonPanel.AddSpace(1, 1, expand="b");
        newFormButtonPanel.Pack();
        return newFormButtonPanel;   
        
    def new_form_button_handler(self, event):
        self.AddComponent(self.create_form_panel(), expand="b");
        self.Select(1);
        self.Repack();
    
    def remove_form(self):
        InputPanel.remove_form(self);
        self.Select(0);
        #self.sizer.Remove(self.windows[1]);
        self.sizer.Remove(1);
        del self.windows[1];

