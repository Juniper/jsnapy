sudo pip uninstall -y jsnapy
# sudo pip uninstall -y -r requirements.txt jsnapy
sudo rm /etc/jsnapy/jsnapy.cfg 
sudo python setup.py sdist
sudo pip install dist/jsnapy-0.1.tar.gz  --install-option="--install-data=~/Desktop/test_inst"
cp samples/config_check_no_test.yml ~/Desktop/test_inst/
cp samples/test_xml.yml ~/Desktop/test_inst/testfiles/
jsnapy --snap PRE -f config_check_no_test.yml
jsnapy --snap POST -f config_check_no_test.yml 
jsnapy --check PRE POST -f config_check_no_test.yml 