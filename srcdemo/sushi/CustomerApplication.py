# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 14, 2012
@author: blubin
'''

from frontend.roleApplication import RoleApplication;
from frontend.form import Type;
from SushiConstants import theflowname

class PaymentApplication(RoleApplication):
    """ The Payment User Interface """

    def __init__(self):
        super(PaymentApplication, self).__init__(theflowname, "Customer");
        self.register_transition_step("MakePayment", self.payment_from_customer);

    def payment_from_customer(self, stepname, form):
        form.add_html_label('<B>Enter your payment details:</B>')
        form.add_field(Type.SHORTSTRING, "FirstName", labeltext="First Name", initial="First");
        form.add_field(Type.SHORTSTRING, "LastName", labeltext="Last Name", initial="Last");
        form.add_field(Type.CHOICE, "CardType", labeltext="Card Type", choices=['Visa', 'Mastercard', 'AMEX', 'Diners Club'], initial='Visa');
        form.add_field(Type.INTEGER, "Card Number:");
        form.add_field(Type.DATE, "Expiry Date");
        form.add_field(Type.INTEGER, "CVV:");
        form.add_field(Type.CURRENCY, "BillAmount", labeltext="Bill Amount", initial=19.99);
    
if __name__ == '__main__':
    app = PaymentApplication();
    app.MainLoop();