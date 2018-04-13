import os
import signal
import time

from utils import *


class TCPDumpConfig:
    def __init__(self, pcap_output, iface, tcpdump_filter = ''):
        self.pcap_output = pcap_output
        self.iface = iface
        self.tcpdump_filter = tcpdump_filter


class MITMProxyConfig:
    def __init__(self, flow_output, port = 8080):
        self.flow_output = flow_output
        self.port = port


class TCPDump:
    def __init__(self, config):
        self.config = config
        self.p_tcpdump = None

    def start(self):
        cmd = "tcpdump -U -w %s -i %s %s" % (self.config.pcap_output, self.config.iface, self.config.tcpdump_filter)
        self.p_tcpdump = sp.Popen(cmd, stdout = sp.PIPE, shell = True)
        time.sleep(5)

    def stop(self):
        try:
            self.p_tcpdump.send_signal(signal.SIGINT)
            time.sleep(15)
            os.killpg(os.getpgid(self.p_tcpdump.pid), signal.SIGINT)
            self.p_tcpdump.kill()
        except:
            pass


class MITMProxy:
    def __init__(self, config):
        self.config = config
        self.p_mitmproxy = None

    def start(self):
        cmd = "mitmdump -z -T -w %s" % self.config.flow_output
        self.p_mitmproxy = sp.Popen(cmd, stdout = sp.PIPE, shell = True, preexec_fn = os.setsid)
        time.sleep(5)

    def stop(self):
        try:
            self.p_mitmproxy.send_signal(signal.SIGINT)
            time.sleep(15)
            os.killpg(os.getpgid(self.p_mitmproxy.pid), signal.SIGINT)
            self.p_mitmproxy.kill()
        except:
            pass
