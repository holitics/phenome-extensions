# miner_dumper.py, Copyright (c) 2019 Holitics/Phenome Project, Nicholas Saparoff

# Original Implementation

import sys, time, datetime
import argparse

from phenome.extensions.lib.pycgminer import CgminerAPI


class MinerDumper():

    def __init__(self):

        self.last_output = None


    def __do_miner_api_call(self, cgminer_obj, command_name, args):

        print("\n'{\"command\": \"" + command_name + "\"}':")
        output = cgminer_obj.call(command_name, args)
        print(output)

        self.last_output = output

    def __build_arg_parser(self):

        parser = argparse.ArgumentParser(
            description="Miner API Dumper, Copyright 2019 Phenome Project / MinerMedic (TM)",
            prog='miner_dumper',
            epilog="Happy Dumping!")
        parser.add_argument('-ip', help='IP ADDRESS of CryptoMiner to target (e.g. 10.1.1.150)')
        parser.add_argument('-port', nargs="?", help='API PORT of CryptoMiner to target', default=4028, type=int)
        parser.add_argument('-cmd', nargs="?", help='Specific command to send API (e.g. "stats", "devs")')
        parser.add_argument('-plcmd', nargs="?", help='Payload command to send API (default is "command")')
        parser.add_argument('-baikal', help='Specify a Baikal Miner', action='store_true')
        parser.add_argument('-antminer', help='Specify a BitMain Antminer', action='store_true')
        parser.add_argument('-claymore', help='Specify a Claymore Miner', action='store_true')
        parser.add_argument('-avalon', help='Specify an Avalon Miner', action='store_true')

        return parser

    def get_last_response(self):
        return self.last_output

    def contact(self, passed_args):

        # init defaults
        ip = '127.0.0.1'
        port = 4028
        api_command = None
        payload_command = "command"
        has_summary = True
        has_devs = False
        has_pools = True
        has_stats = True
        has_getstat1 = False

        # build a parser
        parser = self.__build_arg_parser()

        # parse the args
        if passed_args is not None:
            args = parser.parse_args(passed_args)
        else:
            # will take sys.argv by default
            args = parser.parse_args()

        if args.ip:
            ip = args.ip

        if args.port:
            port = args.port

        if args.cmd:
            api_command = args.cmd

        if args.plcmd:
            payload_command = args.plcmd

        if args.antminer:
            # defaults should work
            pass

        if args.baikal:
            has_stats = False
            has_devs = True

        if args.avalon:
            has_stats = True
            has_summary = True
            has_devs = True
            has_pools = True

        if args.claymore:
            payload_command = "method"
            has_devs = False
            has_stats = False
            has_getstat1 = True
            has_pools = False
            has_summary = False
            port = 3333

        # now execute the API calls
        cgminer = CgminerAPI(host=ip, port=port, payload_command=payload_command)

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        print("---------- MINER DUMPER OUTPUT ON IP {} PORT {} at {} ----------".format(ip, port, st))

        if api_command is not None:

            # call only that one
            output = self.__do_miner_api_call(cgminer, api_command, None)

        else:

            if has_stats:
                try:
                    self.__do_miner_api_call(cgminer, 'stats', None)
                except:
                    pass

            if has_devs:
                try:
                    self.__do_miner_api_call(cgminer, 'devs', None)
                except:
                    pass

            if has_summary:
                try:
                    self.__do_miner_api_call(cgminer, 'summary', None)
                except:
                    pass

            if has_getstat1:
                try:
                    self.__do_miner_api_call(cgminer, 'miner_getstat1', None)
                except:
                    pass

            if has_pools:
                try:
                    self.__do_miner_api_call(cgminer, 'pools', None)
                except:
                    pass


if __name__ == '__main__':

    ####### MAIN PROGRAM STARTS HERE #######

    dumper = MinerDumper()
    dumper.contact(None)