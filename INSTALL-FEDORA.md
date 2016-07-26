### Installation on stock Fedora

The following are instructions for setting up a system starting from a stock system images.

These instructions were tested on a 64-bit systems from https://github.com/opscode/bento.

Operating Systems
---------------
- Fedora 19
- Fedora 20

#### Step 1: Install packages for Junos JSNAPy

    sudo yum install -y python-pip python-devel libxml2-devel libxslt-devel gcc openssl libffi-devel
	
#### Step 2: Install Junos JSNAPy

    sudo pip install git+https://github.com/Juniper/jsnapy.git
