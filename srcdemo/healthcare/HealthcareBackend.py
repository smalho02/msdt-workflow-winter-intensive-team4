# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 13, 2012
@author: blubin
'''

from backend.backend import Backend;
from workflow.task import Task;
from workflow.result import Result;
from workflow.flowData import Status;
from HealthcareConstants import theflowname

class HealthcareBackend(Backend):
   
    def __init__(self): 
        Backend.__init__(self, theflowname, dashboard=True);

    def wire(self):
        self.register_result_listener("Reception", "PatientArrival", self.patient_arrival_complete)
        self.register_result_listener("PhysicianAsst", "Admit", self.admit_complete)
        self.register_result_listener("Physician", "Examine", self.examine_complete)
        self.register_result_listener("Physician", "IsPrescriptionNeeded", self.is_prescription_needed_complete)
        self.register_result_listener("Physician", "WritePrescription", self.write_prescription_complete)
        self.register_joined_listener([("Pharmacist", "FillPrescription", Result), ("Physician", "IsPrescriptionNeeded", Result, Status.COMPLETE)], self.fill_prescription_predicate, self.fill_prescription_complete)

    def patient_arrival_complete(self, results):
        for result in results:
            task = Task.construct_from_result(result, "PhysicianAsst", "Admit");
            self.workflow.add(task);
            self.workflow.update_status(result, Status.COMPLETE);

    def admit_complete(self, results):
        for result in results:
            task = Task.construct_from_result(result, "Physician", "Examine");
            self.workflow.add(task);
            self.workflow.update_status(result, Status.COMPLETE);

    def examine_complete(self, results):
        for result in results:
            task = Task.construct_from_result(result, "Physician", "IsPrescriptionNeeded");
            task.set_field('PrescriptionNumber', 1);
            self.workflow.add(task);
            copyFields =['FirstName','LastName','Birthday','InsuranceCompany','CoPay'];
            task = Task.construct_from_result(result, "Billing", "BillInsurance", copy=copyFields);
            self.workflow.add(task);
            self.workflow.update_status(result, Status.COMPLETE);

    def is_prescription_needed_complete(self, results):
        for result in results:
            if result.data['IsPrescriptionNeeded'] == 1:
                #Add task to write the needed prescrption
                task = Task.construct_from_result(result, "Physician", "WritePrescription");
                self.workflow.add(task);
                #Add task to ask if we need another prescription
                task = Task.construct_from_result(result, "Physician", "IsPrescriptionNeeded");
                task.set_field('PrescriptionNumber',result.get_int_field('PrescriptionNumber')+1);
                task.remove_field('IsPrescriptionNeeded');
                self.workflow.add(task);
            self.workflow.update_status(result, Status.COMPLETE);

    def write_prescription_complete(self, results):
        for result in results:
            copyFields =['FirstName','LastName','Birthday','DrugName','Dose','Frequency','Refills','IsGenericAcceptable', 'PrescriptionNumber'];
            task = Task.construct_from_result(result, "Pharmacist", "FillPrescription", copy=copyFields);
            self.workflow.add(task);
            self.workflow.update_status(result, Status.COMPLETE);

    def fill_prescription_predicate(self, results):
        # One of the results should have isprescriptionneeded=FALSE.  That is the total number.  Ensure we have that number.
        lastpreneeded = [result for result in results if (result.stepname == "IsPrescriptionNeeded" and not result.get_bool_field('IsPrescriptionNeeded'))];
        if len(lastpreneeded) == 0:
            return False;
        # One less than the "No" is the number we are looking for:
        numprescriptions = lastpreneeded[0].get_int_field("PrescriptionNumber")-1;
        # Get the filled ones:
        filled = [result for result in results if result.stepname == "FillPrescription"];
        # If they are all filled, we are done:
        return len(filled) == numprescriptions;

    def fill_prescription_complete(self, results):
        # Get the filled ones:
        filled = [result for result in results if result.stepname == "FillPrescription"];
        
        if len(filled) > 0:
            copyFields =['FirstName','LastName','Birthday'];
            appendFields = ['PrescriptionNumber', 'DrugName','GenericName','Refills'];
            addFields = ['TotalCharge'];
            task = Task.construct_from_results(filled, "Pharmacist", "DispensePrescription", copy=copyFields, append=appendFields, add_fields=addFields);
            self.workflow.add(task);
        for result in filled:
            self.workflow.update_status(result, Status.COMPLETE);

if __name__ == '__main__':
    backend = HealthcareBackend();