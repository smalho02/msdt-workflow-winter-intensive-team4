'''
The Kitchen User Interface for the Restaurant bar workflow (Winter Intensives Lab 5)

This is where you define the fields that appear on the screen (application) the Kitchen
sees and tell WMP how this application (user interface) fits into the overall workflow.

Note:  the comments here assume you have already read through the comments
in RestaurantBackend.py and OrderTakerApplication.py and made your edits there.
'''

from frontend.roleApplication import RoleApplication
from frontend.form import Type
from SushiConstants import theflowname

class KitchenApplication(RoleApplication):
    '''
    The KitchenApplication "class" is a collection of the "methods" (functions) that 
    define the elements of the order taker application.  
    
    An application will always include the method __init__ and at least one
    method to define a form that the user of this application will use.
    '''

    def __init__(self):
        '''
        Declare this application to be part of a given work flow and specify its role in that workflow.
        '''
        # Declare this application to be part of a given workflow, and responsible for a given role:
        # !!! Modify the following to use the actual role name you need...
        super(KitchenApplication, self).__init__(theflowname, "Kitchen") 
        
        # Declare any tasks that this role is able to perform:
        # !!! Modify to use actual task name and name_fields:
        self.register_transition_step("MakeOrder", self.prepare_order_from_customer, name_fields=["sequence", "Name"])


    def prepare_order_from_customer(self, stepname, form):
        '''
        Defines the data entry form for the Kitchen application.
        This form appears once the Kitchen selects one of the pending orders from a list.
        '''
        
        # !!! Use one or more fields from order to define label...
        #form.add_task_label(fields=["Appetizer", "Main", "Dessert", "Beverage"]) 
        # !!! Add any static labels or fields you want to include in this form...

        name = str(form.task.get_field('Name'))
        form.add_static_label("Name: " + name)
        appetizer = str(form.task.get_field('Appetizer'))
        form.add_static_label("Appetizer: " + appetizer)
        main = str(form.task.get_field('Main'))
        form.add_static_label("Main: " + main)
        dessert = str(form.task.get_field('Dessert'))
        form.add_static_label("Dessert: " + dessert)
        beverage = str(form.task.get_field('Beverage'))
        form.add_static_label("Beverage: " + beverage)

if __name__ == '__main__':
    #starts up the KitchenApplication:
    app = KitchenApplication()
    #Start interacting with the user:
    app.MainLoop()