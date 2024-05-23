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
    """ The PharmacistAsst User Interface """

    def __init__(self):
        super(PhysicianAsstApplication, self).__init__(theflowname, "Pharmacist");
        self.register_transition_step("FillPrescription", self.fill_prescription_form_creator, name_fields=["sequence", "FirstName", "LastName", "Birthday", "PrescriptionNumber"]);
        self.register_sink_step("DispensePrescription", self.dispense_prescription_form_creator, name_fields=["sequence", "FirstName", "LastName", "Birthday", "PrescriptionNumber"], form_handler=self.dispense_prescription_form_handler);

    def fill_prescription_form_creator(self, stepname, form):
        form.add_task_label(fields=["FirstName", "LastName", "Birthday"]);
        form.add_field(Type.BOOLEAN, "IsGenericUsed");
        form.add_field(Type.SHORTSTRING, "GenericName");
        form.add_field(Type.CURRENCY, "TotalCharge");
    
    def dispense_prescription_form_creator(self, stepname, form):
        form.add_task_label(fields=["FirstName", "LastName", "Birthday"]);
        form.add_field(Type.CURRENCY, "CoPay");

    def dispense_prescription_form_handler(self, stepname, data, task):
        data["InsuranceCharge"] = task.get_int_field("TotalCharge") - data["CoPay"];
        RoleApplication.default_sink_form_handler(self, stepname, data, task);

if __name__ == '__main__':
    app = PhysicianAsstApplication();
    app.MainLoop();