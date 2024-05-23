'''
The Order Taker User Interface for the Restaurant bar workflow (Winter Intensives Lab 5)

This is where you define the fields that appear on the screen (application) the order
taker sees and tell WMP how this application (user interface) fits into the overall
workflow.

Note:  the comments here assume you have already read through the comments
in RestaurantBackend.py and made your edits there.
'''

# these next few lines import some of the WMP functions we will
# use in this file.
from frontend.roleApplication import RoleApplication
from frontend.form import Type
from SushiConstants import theflowname

class OrderTakerApplication(RoleApplication):
    '''
    The OrderTakerApplication "class" is a collection of the "methods" (functions) that 
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
        super(OrderTakerApplication, self).__init__(theflowname, "Server") 
        # Declare any tasks that this role is able to perform:
        # !!! Modify to use actual name for this task...
        self.register_source_sstep("TakeOrder", self.take_order_form_customer) 

    def take_order_form_customer(self, stepname, form):
        '''
        This method does the actual work of building the user interface.
        '''
        # !!! improve this text...
        form.add_html_label('<B>Enter new Restaurant order information:</B>')
        form.add_field(Type.SHORTSTRING, "Name", labeltext="Name", initial="Name");
        form.add_field(Type.CHOICE, "Appetizer", labeltext="Appetizer", choices=['Sexy Sushi', 'Sashimi in a Bikini', 'Tasty Takoyaki', 'Wakame Salad']);
        form.add_field(Type.CHOICE, "Main", labeltext="Main", choices=['Chicken Bento', 'Ramen', 'Vegetable Soba', 'Beef Teriyaki']);
        form.add_field(Type.CHOICE, "Dessert", labeltext="Dessert", choices=['Strawberry Cheesecake', 'Matcha Ice Cream', 'Tiramisu', 'Brownies']);
        form.add_field(Type.CHOICE, "Beverage", labeltext="Beverage", choices=['Green Tea', 'Soft Drinks', 'Beer', 'Wine']);

        # !!! Add at least two fields here, along with any additional static labels you need...

if __name__ == '__main__':
    #starts up the OrderTakerApplication:
    app = OrderTakerApplication()
    #Start interacting with the user:
    app.MainLoop()