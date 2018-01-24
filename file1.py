from jnpr.jsnapy.jsnapy import SnapAdmin
from pprint import pprint
js = SnapAdmin()
cfg_file = 'main.yml'

js.snap(cfg_file,"pre123")
#js.snap(cfg_file,"post")
# snapvalue =js.snapcheck(cfg_file, "post_jam")
snapvalue = js.check(cfg_file, "pre123", "/Users/jasminder/jsnapy/snapshots/jammy.xml")
#
# for snapcheck in snapvalue:
#     print "\n -----------snapcheck----------"
#     print "Tested on", snapcheck.device
#     print "Final result: ", snapcheck.result
#     print "Total passed: ", snapcheck.no_passed
#     print "Total failed:", snapcheck.no_failed
#     pprint(snapcheck.test_results)
