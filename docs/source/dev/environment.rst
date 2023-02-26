
Setting up a Development Environment
====================================

This page includes instructions on how to set up a developer environment.
These instructions are not intended for end-users; you only need to follow 
them instructions if you're a Chimera developer.

Initial Setup
-------------

Assuming you've cloned the repository, perform the following steps from inside
the repository's root. Please note that these steps only have to be performed
once.


#. 
   Create a virtual environment and install Chimera (and dependencies).

   .. code-block::

      python3 -m venv venv
      source venv/bin/activate
      pip3 install pip --upgrade
      pip3 install wheel
      pip3 install -r requirements.txt

