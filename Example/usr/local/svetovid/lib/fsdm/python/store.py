# Copyright ##year## AVSystem <avsystem@avsystem.com>
# AVSystem SVD
# Version ##version##
# ALL RIGHTS RESERVED
import json
import socket
import sys
import os


class KvStore:
    def __init__(self, namespace):
        """
        Parameters
        ----------
        namespace: int, str
            The unique namespace to avoid key name collision between
            different objects' implementations. We recommend setting
            it to the Object ID (e.g. namespace=3303).
        """

        self._namespace = str(namespace)

    def _perform_operation(self, op):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            s.connect(os.getenv('FSDM_SERVER_SOCKET', '/tmp/fsdm_local_socket'))
            s.sendall(json.dumps({'store': op}).encode('utf-8'))
            s.shutdown(socket.SHUT_WR)

            CHUNK_SIZE = 4096
            data = b''
            while True:
                chunk = s.recv(CHUNK_SIZE)
                data += chunk
                if len(chunk) < CHUNK_SIZE:
                    break

            response = json.loads(data)
        finally:
            s.close()

        if response['result'] == 'error':
            if isinstance(str, response['details']):
                error_msg = response['details']
            else:
                error_msg = '\n' + '\n- '.join(response['details'])

            raise RuntimeError('Operation failed: %s' % error_msg)

        return response

    def _into_store_key(self, key):
        return '#'.join((self._namespace, key))

    def _from_store_key(self, key):
        prefix = self._into_store_key('')
        assert key.startswith(prefix)
        return key[len(prefix):]

    def get_many(self, keys):
        store_keys = [self._into_store_key(k) for k in keys]
        result = self._perform_operation(
            {'get': store_keys}).get('details', dict())
        kv_result = {}
        for k in store_keys:
            if k in result:
                kv_result[self._from_store_key(k)] = result[k]

        return kv_result

    def set_many(self, keys_values):
        store_keys = {}
        for k, v in keys_values.items():
            store_keys[self._into_store_key(k)] = v

        self._perform_operation({'set': store_keys})

    def delete_many(self, keys):
        store_keys = [self._into_store_key(k) for k in keys]
        self._perform_operation({'delete': store_keys})

    def get(self, key, default=None):
        return self.get_many((key,)).get(key, default)

    def set(self, key, value):
        self.set_many({key: value})

    def delete(self, key):
        self.delete_many((key,))
