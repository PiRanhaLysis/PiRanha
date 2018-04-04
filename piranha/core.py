import json
import logging

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
        logging.basicConfig(level = logging.INFO, format = 'PiRanha - %(levelname)s: %(message)s')

    def register_smartphone(self, adb, brand):
        logging.info('Start smartphone registration')
        adb.connect()
        id = adb.get_id()
        imei = adb.get_property('ro.wind_imei')
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
            'serial': imei,
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
                raise ConnectionError('Unable register the smartphone')
        else:
            logging.info('✅️ smartphone registered')
