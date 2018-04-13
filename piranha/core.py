import json
import logging
import os
import subprocess
import sys

import requests


class PiRanha:
    def __init__(self, host, token):
        """
        Instantiate a new PiPrecious connector.
        :param host: PiPrecious host e.g. http://localhost:8000
        :param token: PiPrecious authentication token
        """
        self.host = host
        self.access_token = token
        self.experiment = None
        self.application = None
        self.apk_path = None
        logging.basicConfig(level = logging.INFO, format = 'PiRanha - %(levelname)s: %(message)s')

    def register_smartphone(self, adb, brand):
        logging.info('Start smartphone registration')
        adb.connect()
        id = adb.get_id()
        if len(id.strip()) == 0:
            logging.fatal('No smartphone found')
            sys.exit(-1)

        imei = adb.get_imei()
        phone_number = adb.get_phone_number()
        serial = adb.get_android_id()
        name = adb.get_property('ro.product.model')
        fingerprint = adb.get_property('ro.build.fingerprint')
        logging.info(' - ID:     %s' % id)
        logging.info(' - IMEI:   %s' % imei)
        logging.info(' - Name:   %s' % name)
        logging.info(' - Label:  %s' % fingerprint)
        props = adb.get_props()
        smartphone = {
            'name': name,
            'brand': brand,
            'serial': serial,
            'imei': imei,
            'phone_number': phone_number,
            'label': fingerprint,
            'raw_parameters': props
        }
        url = '%s/api/smartphone' % self.host
        r = requests.post(url, json.dumps(smartphone))
        if r.status_code > 210:
            if ' already exists' in r.text:
                logging.info('⚠️ smartphone already registered')
            else:
                logging.fatal('Unable register the smartphone')
                sys.exit(-1)
        else:
            logging.info('✅️ smartphone registered')

    def get_experiment(self, experiment_id):
        if self.experiment is not None:
            return self.experiment
        url = '%s/api/experiment/%s/' % (self.host, experiment_id)
        r = requests.get(url)
        if r.status_code > 200:
            logging.fatal('Unable to get experiment details')
            sys.exit(-1)
        self.experiment = r.json()
        return self.experiment

    def get_application(self, experiment):
        if self.application is not None:
            return self.application
        url = '%s/api/application/%s/' % (self.host, experiment['application'])
        r = requests.get(url)
        if r.status_code > 200:
            logging.fatal('Unable to get application details')
            sys.exit(-1)
        self.application = r.json()
        return self.application

    def download_apk(self, destination, experiment):
        """
        Download the APK into the provided destination path.
        :param destination: path to store the downloaded APK
        :return: path of the APK e.g. /tmp/fr.meteo.apk
        """
        url = '%s/api/application/%s/apk' % (self.host, experiment['application'])
        local_filename = '%s.apk' % self.experiment['application']
        r = requests.get(url, stream = True, headers = {'Authorization': 'Token %s' % self.access_token})
        local_path = os.path.join(destination, local_filename)
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size = 1024):
                if chunk:
                    f.write(chunk)
        ret_code = r.status_code
        if ret_code != 200:
            logging.fatal('Unable to download the APK')
            sys.exit(-1)
        logging.info('✅️ APK successfully downloaded to %s' % local_path)
        return local_path

    def check_smartphone(self, adb, experiment):
        if experiment['smartphone'] is None:
            logging.info('⚠️ No smartphone specified - check ignored')
            return True
        android_id = adb.get_android_id()
        if android_id is None:
            logging.fatal('❌ No smartphone connected')
            sys.exit(-1)
        url = '%s/api/smartphone/%s/' % (self.host, self.experiment['smartphone'])
        r = requests.get(url, stream = True, headers = {'Authorization': 'Token %s' % self.access_token})
        if r.status_code != 200:
            logging.fatal('❌ Unable to retrieve smartphone details')
            sys.exit(-1)
        smartphone = r.json()
        if android_id == smartphone['serial']:
            logging.info('✅️ Correct smartphone connected')
            return True
        else:
            logging.fatal('❌ Wrong smartphone connected')
            sys.exit(-1)

    def create_session(self, experiment, name):
        url = '%s/api/experiment/%s/session' % (self.host, experiment['id'])
        session = {
            'name': name,
            'experiment': experiment['id']
        }
        r = requests.post(url, json.dumps(session))
        if r.status_code != 201:
            logging.fatal('Unable to create the session')
            sys.exit(-1)
        logging.info('✅️ Session [%s] created' % name)
        return r.json()

    def start_tranparent_routing(self):
        cmd = 'sh /usr/share/PiRogue/proxy/transparent.sh'
        try:
            subprocess.check_call(cmd, shell = True, stdout = subprocess.PIPE)
        except:
            logging.fatal('Unable to start transparent routing')
            sys.exit(-1)

    def stop_tranparent_routing(self):
        cmd = 'sh /usr/share/PiRogue/proxy/stop_transparent.sh'
        try:
            subprocess.check_call(cmd, shell = True, stdout = subprocess.PIPE)
        except:
            logging.fatal('Unable to stop transparent routing')
            sys.exit(-1)

    def upload_pcap(self, pcap_file, sesssion):
        """
        Upload the given PCAP file. The file has be in the Wireshark PCAP format.
        :param pcap_file: path to the local PCAP file
        """
        url = '%s/api/session/%s/pcap' % (self.host, sesssion['id'])
        with open(pcap_file, 'rb') as f:
            r = requests.post(url, files = {'file': f},
                              headers = {"Authorization": "Token %s" % self.access_token,
                                         "Content-Disposition": "attachment; filename=%s" % os.path.basename(pcap_file)}
                              )
            ret_code = r.status_code
            if ret_code != 201:
                logging.fatal('Unable to upload the PCAP file')
                sys.exit(-1)
            logging.info('✅️ PCAP file uploaded')

    def upload_flow(self, flow_file, session):
        """
        Upload the given PCAP file. The file has be in the MITMDump FLOW format.
        :param flow_file: path to the local FLOW file
        """
        url = '%s/api/session/%s/flow' % (self.host, session['id'])
        with open(flow_file, 'rb') as f:
            r = requests.post(url, files = {'file': f},
                              headers = {"Authorization": "Token %s" % self.access_token,
                                         "Content-Disposition": "attachment; filename=%s" % os.path.basename(flow_file)}
                              )
            ret_code = r.status_code
            if ret_code != 201:
                logging.fatal('Unable to upload the FLOW file')
                sys.exit(-1)
            logging.info('✅️ FLOW file uploaded')
