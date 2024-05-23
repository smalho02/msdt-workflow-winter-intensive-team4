# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

from frontend.roleApplication import RoleApplication;
from frontend.form import Type;
from HealthcareConstants import theflowname

class ReceptionApplication(RoleApplication):
    """ The Reception User Interface """

    def __init__(self):
        super(ReceptionApplication, self).__init__(theflowname, "Reception");
        self.register_source_step("PatientArrival", self.patient_arrival_form_creator);

    def patient_arrival_form_creator(self, stepname, form):
        form.add_html_label('<B>Enter new patient information:</B>')
        form.add_field(Type.SHORTSTRING, "FirstName", labeltext="First Name", initial="First");
        form.add_field(Type.SHORTSTRING, "LastName", labeltext="Last Name", initial="Last");
        form.add_field(Type.DATE, "Birthday");
        form.add_static_label("Insurance Information:");
        form.add_field(Type.SHORTSTRING, "InsuranceCompany", labeltext="Insurance Company", initial="Company");
        form.add_field(Type.CHOICE, "InsuranceType", labeltext="Insurance Type", choices=['HMO', 'POS', 'PPO', 'Indemnity'], initial='POS');
        form.add_field(Type.CURRENCY, "CoPay", labeltext="Co-Pay", initial=20);
    
if __name__ == '__main__':
    app = ReceptionApplication();
    app.MainLoop();