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
    """ The Billing User Interface """

    def __init__(self):
        super(PhysicianAsstApplication, self).__init__(theflowname, "Billing");
        self.register_sink_step("BillInsurance", self.bill_insurance_form_creator, name_fields=["sequence", "FirstName", "LastName", "Birthday"], form_handler=self.insurance_form_handler);

    def bill_insurance_form_creator(self, stepname, form):
        form.add_task_label(fields=["FirstName", "LastName", "Birthday"]);
        form.add_field(Type.FLOAT, "TotalCharge");

    def insurance_form_handler(self, stepname, data, task):
        data["InsuranceCharge"] = data["TotalCharge"] - task.get_int_field("CoPay");
        RoleApplication.default_sink_form_handler(self, stepname, data, task);

if __name__ == '__main__':
    app = PhysicianAsstApplication();
    app.MainLoop();