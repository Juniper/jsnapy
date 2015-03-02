from jnpr.junos import Device
import yaml


class Hosts:

    def login(self, args, main_file, output_file):
        self.hostname_list = []
        devices = {}
        if args.hostname is None:
            k = main_file['hosts'][0]
            if k.__contains__('include'):
                lfile = k['include']
                login_file = open(lfile, 'r')
                dev_file = yaml.load(login_file)
                gp = k['group']

                dgroup = [i.strip() for i in gp.split(',')]
                for dgp in dev_file:
                    if dgroup[0] == 'all' or dgp in dgroup:
                        for val in dev_file[dgp]:
                            hostname = val.keys()[0]
                            self.hostname_list.append(hostname)
                            username = val[hostname]['username']
                            password = val[hostname]['passwd']
                            snap_files = hostname + '_' + output_file
                            dev_obj = self.connect(
                                hostname,
                                username,
                                password)
                            devices[dev_obj] = snap_files

            else:
                hostname = k['devices']
                username = k['username']
                password = k['passwd']
                self.hostname_list.append(hostname)
                dev_obj = self.connect(hostname, username, password)
                snap_files = hostname + '_' + output_file
                devices[dev_obj] = snap_files

# if login credentials are given from command line
        else:
            hostname = args.hostname
            password = args.passwd
            username = args.login
            self.hostname_list.append(hostname)
            snap_files = hostname + '_' + output_file
            dev_obj = self.connect(hostname, username, password)
            devices[dev_obj] = snap_files
        return (devices)

# function to connect to device
    def connect(self, hostname, username, password):
        print "connecting to device", hostname, ".............."
        dev = Device(host=hostname, user=username, passwd=password)
        return dev
