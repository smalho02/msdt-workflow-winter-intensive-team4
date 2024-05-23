# This code is part of the MWP System
# Copyright (c) 2012 Benjamin Lubin (blubin@bu.com) 
# Published under and subject to the GPLv2 license available at http://www.gnu.org/licenses/gpl-2.0.html

'''
Created on Dec 18, 2012
@author: blubin
'''

from frontend.roleApplication import RoleApplication;
from frontend.form import Type;
from SushiConstants import theflowname

class KitchenApplication(RoleApplication):
    """ Order Completed User Interface """

    def __init__(self):
        super(KitchenApplication, self).__init__(theflowname, "ServeOrder");
        self.register_sink_step("Server", self.order_ready, name_fields=["Sequence", "Name"])

    def order_ready(self, stepname, form):
        sequence = str(form.task.get_field('Sequence'))
        form.add_static_label("Order number " + sequence + " is ready to pick up./n Thank you for ordering with us.")

if __name__ == '__main__':
    app = KitchenApplication();
    app.MainLoop();