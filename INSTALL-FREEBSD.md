### Installation on stock FreeBSD

The following are instructions for setting up a system starting from a stock system images.

These instructions were tested on a 64-bit systems from https://github.com/opscode/bento.

Operating Systems
---------------
- FreeBSD 9.2

#### Step 1: Install packages for Junos JSNAPy

    sudo pkg_add -r py27-pip libxml2 libxslt
	
#### Step 2: Install Junos JSNAPy

    sudo pip install git+https://github.com/Juniper/jsnapy.git
    
#### Step 3: Verify 

Enjoy!
