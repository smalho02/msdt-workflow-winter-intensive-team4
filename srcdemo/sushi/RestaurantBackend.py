'''
Back end for the Restaurant bar workflow (Winter Intensives Lab 5)

This file is where you "wire" together the steps in the process.
'''

# these next few lines import some of the WMP functions we will
# use in this file.
from backend.backend import Backend
from workflow.task import Task
from workflow.result import Result 
from workflow.flowData import Status
from SushiConstants import theflowname

class RestaurantBackend(Backend):
    '''
    The RestaurantBackend "class" is a collection of the "methods" (functions) that do the actual
    wiring together of the steps in the Restaurant bar process.
    
    A back end will always include the methods __init__ and wire and will also include a method
    to handle each event that occurs in the process.  For Lab 5 we have set up the two additional
    methods you need:  drink_order_taken and drink_prepared.
    
    See instruction documentation to see what you need to do.
    '''
   
    def __init__(self): 
        # Specify the workflow name:       
        Backend.__init__(self, theflowname)  

    def wire(self):
        '''
        The wire method is where we tell MWP which tasks to keep track of.
        To register a task, you will need to add a line of code that looks
        like this:
        self.register_result_listener("RoleName", "TaskName", self.method_name)
        Where: RoleName is the person who did the task
               TaskName is the name of the task they did
               self.method_name refers to a method in this class which should respond to
                                the task being completed.
        '''
        self.register_result_listener("Server", "TakeOrder", self.order_taken)
        self.register_result_listener("Customer", "MakePayment", self.payment_received)
        self.register_result_listener("Kitchen", "MakeOrder", self.order_prepared)
        # !!! add a line of code here to register the step where a drink order is taken.
        # !!! add a line of code here to register the step where a drink is prepared.
    
    def order_taken(self, results):
        for result in results:
            task = Task.construct_from_result(result, "Customer", "MakePayment");
            self.workflow.add(task);
            self.workflow.update_status(result, Status.COMPLETE)

    def payment_received(self, results):
        for result in results:  # repeat the following actions for each result
            # !!! Fix the line below...
            task = Task.construct_from_result(result, "Kitchen", "MakeOrder");
            self.workflow.add(task) # add the new task to the workflow
            self.workflow.update_status(result, Status.COMPLETE)

    def order_prepared(self, results):
        '''
        This method is called after the Kitchen has prepared the drink.  
        In our very simple workflow this is the last step in the process, 
        which means that this method has a very simple job:  it just needs to mark 
        the status of the Kitchen's task (stored in the results variable) as Complete.  
        '''
        for result in results:
            self.workflow.update_status(result, Status.COMPLETE)

'''
Finally, this last bit of code is fine as it is and you do not need to change it.
It initialize the backend by running the __init__ method
of the RestaurantBackend class (above), among other things.
'''
if __name__ == '__main__':
    backend = RestaurantBackend()