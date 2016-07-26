### Installation on stock Ubuntu and Debian

The following are instructions for setting up a system starting from stock system images.

These instructions were tested on a 64-bit systems from https://github.com/opscode/bento, and using the _Junos PyEZ_ library version 1.3.1.

Operating Systems
---------------
- Ubuntu 12.04
- Ubuntu 12.10
- Ubuntu 13.10
- Ubuntu 14.04
- Debian 7.4
- Debian 8.4


#### Step 1: Update package list

	sudo apt-get update

#### Step 2: Install OS packages required by Junos JSNAPy and it's pre-requisite Python packages

    sudo apt-get install -y --force-yes python-dev libxslt1-dev libssl-dev libffi-dev

#### Step 3: Install the pip package manager from source

    wget https://bootstrap.pypa.io/get-pip.py -O - | sudo python
	
#### Step 4: Install Junos JSNAPy

    sudo pip install git+https://github.com/Juniper/jsnapy.git
    
#### Step 5: Verify 

Enjoy!
