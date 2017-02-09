# -*- coding: utf-8 -*-


class BaseConfig(object):
    # Vultr
    APIKEY = ''  # must be set at instance.config.Config
    HOSTNAME = 'ssserver'
    LABEL = 'SSSERVER'
    SCRIPT_NAME = 'SSSERVER'
    SSHKEY_NAME = ''  # optional, set at instance.config.Config
    # https://api.vultr.com/v1/regions/list
    DCID = 40  # Los Angeles: 5, Tokyo: 25, Singapore: 40
    VPSPLANID = 29  # $5/mo
    OSID = 231  # Ubuntu 16.10 x64

    # ssserver config
    SSSERVER_ADDR = '0.0.0.0'
    SSSERVER_PORT = 8388
    SSSERVER_PASSWORD = ''  # set at instance.config.Config
    SSSERVER_METHOD = 'aes-256-cfb'
    SSSERVER_TIMEOUT = 500
    SSSERVER_WORKERS = 4

    # kcptun server config
    KCPTUN_LISTEN = 18388
    KCPTUN_TARGET = '127.0.0.1:8388'
    KCPTUN_KEY = ''  # set at instance.config.Config
    KCPTUN_CRYPT = 'aes-192'
    KCPTUN_MODE = 'fast2'
