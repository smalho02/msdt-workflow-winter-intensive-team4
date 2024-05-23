# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

import unicodedata
from wax import Panel;
from wax.scrollpanel import ScrollPanel;
from wax import Label;
from wax import TextBox;
from wax import Font;
from wax import CheckBox;
from wax import DropDownBox;
from wax.maskedtextbox import MaskedTextBox;
from wax.tools.spinbox import SpinBox;
from wax.tools.spinboxdouble import SpinBoxDouble;
from wax.tools.datepicker import DatePicker;
from wax.htmlwindow import HTMLWindow;
from collections import OrderedDict;
from workflow.util import convert_fieldname_to_db;
from workflow.util import enum;

Type = enum('SHORTSTRING', 'LONGSTRING', 'INTEGER', 'FLOAT', 'CURRENCY', 'DATE', 'BOOLEAN', 'CHOICE');

def default_title_renderer(task, fields):
    s = "<b>";
    for field in fields:
        s = s + str(task.get_field(field)) + " ";
    s = s + ":</b><br>";
    return s;

def default_fields_renderer(task, fields):
    s = "<table border=1 padding=1>";
    cfields = [convert_fieldname_to_db(f) for f in fields];
    count = 0;
    numcols=3;
    if not len(cfields) == len(task.data.keys()):
        s = s + "<tr>";
        for i in range(0, numcols):
            s = s + "<th>Field</th><th>Value</th>";
        s = s + "</tr>";
    for field in task.data.keys():
        if field in cfields:
            continue;
        if count % numcols == 0:
            s = s + "<tr>";
        val = task.get_field(field)
        if val == None:
            val = ""
        s = s + "<td><i>" + str(field) +" </i></td><td><b>" + str(val) + "<b></td>";
        if count % numcols == 0:
            s = s + "</tr>";
        count = count + 1;
    s = s + "</table>";
    return s;

class Form(ScrollPanel):
    
    def __init__(self, parent, stepname, form_creator, form_handler, task=None, direction="v", **kwargs):
        self.stepname = stepname;
        self.form_creator = form_creator;
        self.form_handler = form_handler;
        self.task = task;
        self.controls = OrderedDict();
        self.fieldtypes = OrderedDict();
        ScrollPanel.__init__(self, parent, direction,tab_traversal=True, **kwargs)
        
    def Body(self):
        self.form_creator(self.stepname, self);
        self.Pack();

    def get_task_label(self, title_renderer=default_title_renderer, fields_renderer=default_fields_renderer, **kwargs):
        label = title_renderer(self.task, **kwargs);
        label = label + fields_renderer(self.task, **kwargs);
        return label;
            
    def add_task_label(self, title_renderer=default_title_renderer, fields_renderer=default_fields_renderer, **kwargs):
        label = self.get_task_label(title_renderer, fields_renderer, **kwargs);
        self.add_html_label(labeltext=label);
        
    def add_html_label(self, labeltext="", size=None, **kwargs):
        label = HTMLWindow(self, scroll=False, size=size);
        label.SetPage(labeltext);
        #Setup sizing per https://groups.google.com/forum/?fromgroups=#!topic/wxpython-users/M2FVmlzh0cY
        ir = label.GetInternalRepresentation()
        label.SetSize( (ir.GetWidth(), ir.GetHeight()) ) 
        self.AddComponent(label, expand="h");
    
    def add_static_label(self, labeltext=""):
        label = Label(self, labeltext, size=(600, 20), noresize=1);
        self.AddComponent(label, expand="h");

    def add_field(self, fieldtype, fieldname, labeltext=None, initial=None, choices=[], digits=2, min=-1e9, max=1e9):
        fieldPanel = Panel(self, direction="h");

        if labeltext==None:
            labeltext = fieldname;
        
        # Ensure the field matches the database exactly:
        fieldname = convert_fieldname_to_db(fieldname);
        
        label = Label(fieldPanel, labeltext, size = (100, 20), noresize=1);
        fieldPanel.AddComponent(label);
        
        control = self.get_control(fieldPanel, fieldtype, choices=choices, digits=digits, min=min, max=max);
        if initial != None:
            self.set_control_value(fieldtype, control, initial);
        fieldPanel.AddComponent(control);
        self.fieldtypes[fieldname] = fieldtype;
        self.controls[fieldname] = control;
        
        fieldPanel.Pack();
        self.AddComponent(fieldPanel, expand="h");
    
    def get_control(self, parent, fieldtype, choices, digits, min, max):
        if fieldtype == Type.SHORTSTRING:
            return TextBox(parent, Font=Font("Courier New", 10), Size=(500,20), multiline=0);
        elif fieldtype == Type.LONGSTRING:
            return TextBox(parent, Font=Font("Courier New", 10), Size=(500,100), multiline=1);
        elif fieldtype == Type.INTEGER:
            return SpinBox(parent, min=min, max=max);
        elif fieldtype == Type.FLOAT:
            return SpinBoxDouble(parent, digits=digits, min=min, max=max);
        elif fieldtype == Type.CURRENCY:
            ctl = MaskedTextBox(parent, mask="$#{9}.#{2}", formatcodes="r>-");
            ctl.Font = Font("Courier New", 10);
            ctl.Size = (500,20);
            ctl.SetValue("        0.00");
            return ctl;
        elif fieldtype == Type.DATE:
            return DatePicker(parent, style='dropdown', show_century=1)
        elif fieldtype == Type.BOOLEAN:
            return CheckBox(parent, "");            
        elif fieldtype == Type.CHOICE:
            return DropDownBox(parent, choices=choices, size=(500,20));
        else:
            raise Exception("Unknown constant: " + str(type));

    def set_control_value(self, fieldtype, control, value):
        if fieldtype == Type.SHORTSTRING:
            control.SetValue(value);
        elif fieldtype == Type.LONGSTRING:
            control.SetValue(value);
        elif fieldtype == Type.INTEGER:
            control.SetValue(value);
        elif fieldtype == Type.FLOAT:
            control.SetValue(value);
        elif fieldtype == Type.CURRENCY:
            value = "${0:12.2f}".format(value);            
            control.SetValue(value);
        elif fieldtype == Type.DATE:
            control.SetValue(value);
        elif fieldtype == Type.BOOLEAN:
            control.SetValue(value);
        elif fieldtype == Type.CHOICE:
            control.SetSelection(control.FindString(value));
        else:
            raise Exception("Unknown constant: " + str(type));        
    
    def submit(self):
        data = self.get_data();
        #print data;
        self.form_handler(self.stepname, data, self.task);
        
    def get_data(self):
        ret = OrderedDict();
        for fieldname, control in self.controls.items():
            fieldtype = self.fieldtypes[fieldname];
            data = self.get_field_data(fieldname, fieldtype, control);
            ret[fieldname] = data;
        return ret;

    def get_field_data(self, fieldname, fieldtype, control):        
        if fieldtype == Type.SHORTSTRING:
            return self.get_ascii_string(control);
        elif fieldtype == Type.LONGSTRING:
            return self.get_ascii_string(control);
        elif fieldtype == Type.INTEGER:
            return int(control.GetValue());
        elif fieldtype == Type.FLOAT:
            return float(control.GetValue());
        elif fieldtype == Type.CURRENCY:
            data = self.get_ascii_string(control);
            data = data.replace("$", "");
            data = data.replace(" ", "");  # remove all spaces that might be introduced (viz. in v2.9 of wxPython)
            try:
                return float(data);
            except ValueError:
                raise Exception("Not a numeric string: " + data);
        elif fieldtype == Type.DATE:
            return control.GetValue();
        elif fieldtype == Type.BOOLEAN:
            return bool(control.IsChecked());
        elif fieldtype == Type.CHOICE:
            return control.GetString(control.GetSelection());
        else:
            raise Exception("Unknown constant: " + str(type));
        
    def get_ascii_string(self, control):
            data = control.GetValue();
            data = unicodedata.normalize('NFKD', data).encode('ascii','ignore').decode('ascii');
            return data


