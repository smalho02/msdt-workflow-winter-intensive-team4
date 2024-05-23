# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 18, 2012
@author: blubin
'''

from frontend.roleApplication import RoleApplication;
from frontend.form import Type;
from HealthcareConstants import theflowname

class PhysicianAsstApplication(RoleApplication):
    """ The PhysicianAsst User Interface """

    def __init__(self):
        super(PhysicianAsstApplication, self).__init__(theflowname, "PhysicianAsst");
        self.register_transition_step("Admit", self.patient_admit_form_creator, name_fields=["sequence", "FirstName", "LastName", "Birthday"]);

    def patient_admit_form_creator(self, stepname, form):
        form.add_task_label(fields=["FirstName", "LastName", "Birthday"]);
        form.add_field(Type.FLOAT, "Weight");
        form.add_field(Type.FLOAT, "Temperature");
        form.add_field(Type.SHORTSTRING, "BloodPressure");
    
if __name__ == '__main__':
    app = PhysicianAsstApplication();
    app.MainLoop();