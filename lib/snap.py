from lxml import etree
import os


class Parse:

    def generate_reply(self, test_file, devices):
        self.command_list = []
        self.rpc_list = []
        self.test_included = []
        path = os.getcwd()
        for t in test_file['tests_include']:
            self.test_included.append(t)
            if (test_file[t][0].keys()[0] == 'command'):
                command = test_file[t][0]['command']
                self.command_list.append(command)
                name = '_'.join(command.split())
                for dev in devices:
                    dev.open()
                    rpc_reply = dev.rpc.cli(command, format='xml')
                    ofile = devices[dev] + '_' + name + '.' + 'xml'
                    o_file = path + '/' + 'snapshots' + '/' + ofile
                    with open(o_file, 'w') as f:
                        f.write(etree.tostring(rpc_reply))
            else:
                rpc = test_file[t][0]['rpc']
                self.rpc_list.append(rpc)
                for dev in devices:
                    dev.open()
                    rpc_reply = getattr(dev.rpc, rpc.replace('-', '_'))()
                    ofile = devices[dev] + '_' + rpc + '.' + 'xml'
                    output_file = path + '/' + 'snapshots' + '/' + ofile
                    with open(output_file, 'w') as f:
                        f.write(etree.tostring(rpc_reply))
