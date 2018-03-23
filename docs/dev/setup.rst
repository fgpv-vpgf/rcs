Development Setup
=================

For development we will be using the built in Flask server, no separate web server
required.  CouchDB will also be installed in admin party mode (every connection
has admin rights).

Install `CouchDB <http://couchdb.apache.org/>`_
-----------------------------------------------
#. Run the installer
#. Open a web browser and navigate to http://127.0.0.1:5984/_utils
#. Create a database ``rcs_cache`` (navigate to Overview | Create Database)
#. Create a second database ``rcs_auth``

Configure Python Environment
----------------------------
#. Ensure python is a 3.6.x release
#. Install pip (https://pip.pypa.io/en/latest/installing.html)
#. Install virtualenv ``pip install virtualenv``
#. Clone the repo ``git clone git@github.com:RAMP-PCAR/RCS.git rcs``
#. Create python virtual environment ``virtualenv rcs``
#. Switch to the project directory ``cd rcs``
#. Activate the virtualenv ``scripts\activate``
#. Install the project dependencies ``pip install -r requirements.txt``
#. Make any path changes necessary to ``config.py`` (if you followed the above there should be none)
#. Test the installation ``python3.6 rcs.py`` (this will run a test server on localhost)
#. Seed the database ``python3.6 seed_qa_keys.py``

Set up Development Environment and run RCS locally
--------------------------------------------------
#. Install Vagrant (https://www.vagrantup.com/downloads.html)
#. Clone RCS repo ``git clone https://github.com/fgpv-vpgf/rcs.git``
#. Activate Vagrant ``vagrant up`` (Note: Please ensure a Vagrant file exits)
#. Establish a connection ``vagrant ssh``
#. Change to the Vagrant folder ``cd /vagrant``
#. Activate the programmes required ``. rcs-venv/bin/activate``
#. If vagrant failed at any point, run ``vagrant destroy`` then repeat the previous steps again
#. Run RCS ``python3.6 run.py --listen-all``
#. Go to http://localhost:6101/static/test.html for testing (Note: The port number might be different)
