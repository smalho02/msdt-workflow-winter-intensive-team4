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


class PhysicianApplication(RoleApplication):
    """ The Physician User Interface """

    def __init__(self):
        super(PhysicianApplication, self).__init__(theflowname, "Physician");
        self.register_transition_step("Examine", self.examine_form_creator, name_fields=["sequence", "FirstName", "LastName", "Birthday"]);
        self.register_transition_step("IsPrescriptionNeeded", self.is_prescription_needed_form_creator, name_fields=["sequence", "FirstName", "LastName", "Birthday", 'PrescriptionNumber']);
        self.register_transition_step("WritePrescription", self.write_prescription_form_creator, name_fields=["sequence", "FirstName", "LastName", "Birthday", 'PrescriptionNumber']);

    def examine_form_creator(self, stepname, form):
        form.add_task_label(fields=["FirstName", "LastName", "Birthday"]);
        form.add_field(Type.LONGSTRING, "History");
        form.add_field(Type.SHORTSTRING, "Diagnosis");

    def is_prescription_needed_form_creator(self, stepname, form):
        form.add_task_label(fields=["FirstName", "LastName", "Birthday"]);
        form.add_field(Type.BOOLEAN, "IsPrescriptionNeeded");
    
    def write_prescription_form_creator(self, stepname, form):
        form.add_task_label(fields=["FirstName", "LastName", "Birthday"]);
        form.add_field(Type.SHORTSTRING, "DrugName");
        form.add_field(Type.SHORTSTRING, "Dose");
        form.add_field(Type.SHORTSTRING, "Frequency");
        form.add_field(Type.INTEGER, "Refills");
        form.add_field(Type.BOOLEAN, "IsGenericAcceptable");

if __name__ == '__main__':
    app = PhysicianApplication();
    app.MainLoop();