from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device

dev1 = Device(host='10.209.16.208', user='regress', password='MaRtInI')
dev1.open()


js = SnapAdmin()

config_file = "/etc/jsnapy/config_single_check.yml"

snapvalue = js.check(config_file, "pre", "post", dev=dev1)
print "snap value is:", snapvalue


for snapcheck in snapvalue:
    print "\n -----------snapcheck----------", snapcheck
    print "Tested on", snapcheck.device
    print "Final result: ", snapcheck.result
    print "Total passed: ", snapcheck.no_passed
    print "Total failed:", snapcheck.no_failed
    pprint(dict(snapcheck.test_details))


config_data = """
hosts:
  - devices: 10.209.16.204
    username : regress
 #   passwd: Embe1mpls
tests:
  - test_no_diff.yml
  - test_delta.yml
  - test_is_equal.yml
# - test_not_less.yml
# - test_not_more.yml

# can use sqlite to store data and compare them
sqlite:
 - store_in_sqlite: True
   check_from_sqlite: True
   database_name: jbb.db
   compare: 1,0

# can send mail by specifying mail
#mail: send_mail.yml


snapvalue = js.snap(config_data, "pre")
print "snap value is:", snapvalue

for snapcheck in snapvalue:
    print "\n -----------snapcheck----------", snapcheck
    print "Tested on", snapcheck.device
    print "Final result: ", snapcheck.result
    print "Total passed: ", snapcheck.no_passed
    print "Total failed:", snapcheck.no_failed
    pprint (dict(snapcheck.test_details))

try:
    print "inside try"
    js.snap(config_data, "pre")
except Exception as ex:
    print "Ex is",ex
    """""
