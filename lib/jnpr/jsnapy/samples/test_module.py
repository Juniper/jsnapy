from jnpr.jsnapy import SnapAdmin
from pprint import pprint
from jnpr.junos import Device

dev = Device(host='10.209.16.206', user='regress', password='MaRtInI' )
dev.open()


js = SnapAdmin()

config_file = "/etc/jsnapy/config_multiple_check.yml"

config_data = """
hosts:
  - devices: 10.209.16.204
    username : root
    passwd: Embe1mpls
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
"""

snapvalue = js.check(config_file, "pre", "post")
print "snap value is:", snapvalue

for snapcheck in snapvalue:
    print "\n -----------snapcheck----------", snapcheck
    print "Tested on", snapcheck.device
    print "Final result: ", snapcheck.result
    print "Total passed: ", snapcheck.no_passed
    print "Total failed:", snapcheck.no_failed
    pprint (dict(snapcheck.test_details))
