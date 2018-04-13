import sys
import tempfile
from optparse import OptionParser

from adb import *
from core import *
from network import TCPDumpConfig, MITMProxyConfig, TCPDump, MITMProxy

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-r', '--register-smartphone', action = 'store_true', dest = 'register_smartphone',
                      default = False, help = 'register a new connected smartphone')
    parser.add_option('-l', '--launch-session', dest = 'experiment_id', help = 'launch a new session')
    parser.add_option('-u', '--base_url', dest = 'base_url', default = 'http://localhost:8000',
                      help = 'PiPrecious base URL')
    parser.add_option('-a', '--adb_path', dest = 'adb_path', default = 'adb',
                      help = 'adb path')

    (options, args) = parser.parse_args()

    p = PiRanha(options.base_url, 'dsfs')

    adb = ADB(options.adb_path)

    if options.register_smartphone:
        input('Connect the smartphone to the PiRogue and press [enter]: ')
        brand = input('Enter the brand name of the smartphone and press [enter]: ')
        p.register_smartphone(adb, brand = brand)

    if options.experiment_id is not None:
        experiment = p.get_experiment(options.experiment_id)
        if experiment is None:
            sys.exit(-1)

        with tempfile.TemporaryDirectory() as tmp:
            # Download APK
            apk_path = p.download_apk(tmp, experiment)
            # Verify connected smartphone meets experiment requirements
            input('Connect the smartphone to the PiRogue and press [enter]: ')
            application = p.get_application(experiment)
            p.check_smartphone(adb, experiment)
            # Create a new session
            name = input('Enter the session name and press [enter]: ')
            session = p.create_session(experiment, name)
            # Set time and date of the smartphone
            adb.set_date_time()
            # Install the application on the smartphone
            adb.install(apk_path)
            # Prepare tcpdump
            pcap_name = '%s.pcap' % session['id']
            pcap_path = os.path.join(tmp, pcap_name)
            tcpdump_configuration = TCPDumpConfig(pcap_path, 'wlan1')
            tcpdump = TCPDump(tcpdump_configuration)
            # Prepare mitmproxy
            flow_name = '%s.flow' % session['id']
            flow_path = os.path.join(tmp, flow_name)
            mitmproxy_configuration = MITMProxyConfig(flow_path)
            mitmproxy = MITMProxy(mitmproxy_configuration)
            # Start network capture
            p.start_tranparent_routing()
            tcpdump.start()
            mitmproxy.start()
            input('Install the CA by browsing http://mitm.it and press [enter]: ')
            # Start the application
            adb.run(application['handle'])

            # Wait until stop if received
            cmd = input('Type "stop" or "cancel" and press [enter]: ')
            # Stop network capture
            tcpdump.stop()
            mitmproxy.stop()
            # Uninstall the application
            adb.kill(application['handle'])
            adb.uninstall(application['handle'])
            if 'stop' in cmd:
                # Upload files
                p.upload_pcap(pcap_path, session)
                p.upload_flow(flow_path, session)
            else:
                # Do nothing
                sys.exit(0)

