# MSDT Workflow

To get this project to run:
* open it in VSCode (i.e., clone it from git)
* type ctrl-shift-P
* type Create Python Environment
* select a "Venv" environment

You are then ready to run the "healthcare demo" by running
* srcdemo/healthcare/HealthcareBackend.py
* srcdemo/healthcare/ReceptionApplication.py
* And each of the othe UIs in that directory
These must each be run in separate consoles, currently
Note that the "Backend" program must be run first.

The programs run in a hub-and-spoke architecture, with 
each "UI application" communicating with the "Backend"
application, which in turn communicates with the database.