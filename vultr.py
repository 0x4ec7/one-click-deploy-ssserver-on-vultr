# -*- coding: utf-8 -*-
import os
import json
import requests
from config.instance.config import Config


def make_request(method, url, data=None):
    resp = requests.request(method,
                            url,
                            data=data,
                            headers={'API-Key': Config.APIKEY})
    return resp


def create_startupscript(name, script):
    url = 'https://api.vultr.com/v1/startupscript/create'
    method = 'POST'
    req_data = {'name': name,
                'script': script}
    resp = make_request(method, url, data=req_data)
    if resp.status_code != 200:
        raise Exception(resp.status_code)
    resp_data = resp.json()
    scriptid = resp_data.get('SCRIPTID')
    return scriptid


def list_startupscript():
    url = 'https://api.vultr.com/v1/startupscript/list'
    method = 'GET'
    resp = make_request(method, url)
    if resp.status_code != 200:
        raise Exception(resp.status_code)
    resp_data = resp.json()
    return resp_data


def destroy_startupscript(scriptid):
    url = 'https://api.vultr.com/v1/startupscript/destroy'
    method = 'POST'
    req_data = {'SCRIPTID': scriptid}
    resp = make_request(method, url, data=req_data)
    if resp.status_code != 200:
        raise Exception(resp.status_code)


def destroy_duplicated_script(name):
    resp_data = list_startupscript()
    for scriptid in resp_data:
        if resp_data[scriptid]['name'] == name:
            print 'Destroy duplicated startupscript: {}.'.format(name)
            destroy_startupscript(scriptid)


def list_sshkey():
    url = 'https://api.vultr.com/v1/sshkey/list'
    method = 'GET'
    resp = make_request(method, url)
    if resp.status_code != 200:
        raise Exception(resp.status_code)
    resp_data = resp.json()
    return resp_data


def get_sshkeyid(name):
    resp_data = list_sshkey()
    for sshkeyid in resp_data:
        if resp_data[sshkeyid]['name'] == name:
            return sshkeyid


def list_server():
    url = 'https://api.vultr.com/v1/server/list'
    method = 'GET'
    resp = make_request(method, url)
    if resp.status_code != 200:
        raise Exception(resp.status_code)
    resp_data = resp.json()
    return resp_data


def destroy_server(subid):
    url = 'https://api.vultr.com/v1/server/destroy'
    method = 'POST'
    req_data = {'SUBID': subid}
    resp = make_request(method, url, data=req_data)
    if resp.status_code != 200:
        raise Exception(resp.status_code)


def destroy_duplicated_server(label):
    resp_data = list_server()
    for subid in resp_data:
        if resp_data[subid]['label'] == label:
            print 'Destroy duplicated server: {}.'.format(label)
            destroy_server(subid)


def create_server(dcid, vpsplanid, osid, scriptid,
                  sshkeyid=None, hostname=None, label=None):
    url = 'https://api.vultr.com/v1/server/create'
    method = 'POST'
    req_data = {'DCID': dcid,
                'VPSPLANID': vpsplanid,
                'OSID': osid,
                'SCRIPTID': scriptid,
                'SSHKEYID': sshkeyid,
                'hostname': hostname,
                'label': label}
    req_data = {k: v for k, v in req_data.iteritems() if v}
    resp = make_request(method, url, data=req_data)
    if resp.status_code != 200:
        raise Exception(resp.status_code)
    resp_data = resp.json()
    subid = resp_data['SUBID']
    return subid


def get_server_info(subid):
    resp_data = list_server()
    if subid in resp_data:
        return resp_data[subid]


def generate_startup_script():
    content = ('#!/bin/sh\n'
               'apt-get install -y shadowsocks\n'
               'mkdir -p /root/log\n'
               'wget https://github.com/xtaci/kcptun/releases/download/'
               'v20170120/kcptun-linux-amd64-20170120.tar.gz '
               '-O /root/kcptun-linux-amd64-20170120.tar.gz\n'
               'tar -zxf /root/kcptun-linux-amd64-20170120.tar.gz -C /root\n'
               '/root/server_linux_amd64 '
               '--listen ":{kcptun_listen}" --target "{kcptun_target}" '
               '--key "{kcptun_key}" --crypt "{kcptun_crypt}" '
               '--mode "{kcptun_mode}" > /root/log/kcptun.log 2>&1 &\n'
               '/usr/bin/ssserver -s "{ssserver_addr}" -p {ssserver_port} '
               '-k "{ssserver_password}" -m "{ssserver_method}" '
               '-t {ssserver_timeout} --workers {ssserver_workers} -q '
               '> /root/log/ssserver.log 2>&1\n')
    return content.format(ssserver_addr=Config.SSSERVER_ADDR,
                          ssserver_port=Config.SSSERVER_PORT,
                          ssserver_password=Config.SSSERVER_PASSWORD,
                          ssserver_method=Config.SSSERVER_METHOD,
                          ssserver_timeout=Config.SSSERVER_TIMEOUT,
                          ssserver_workers=Config.SSSERVER_WORKERS,
                          kcptun_listen=Config.KCPTUN_LISTEN,
                          kcptun_target=Config.KCPTUN_TARGET,
                          kcptun_key=Config.KCPTUN_KEY,
                          kcptun_crypt=Config.KCPTUN_CRYPT,
                          kcptun_mode=Config.KCPTUN_MODE)


def update_shadowsocksx_ng_profile(ip):
    new_profile = {
        "Method": "aes-256-cfb",
        "Remark": "Vultr",
        "Id": "",
        "EnabledKcptun": True,
        "KcptunProfile": {
            "nocomp": False,
            "crypt": Config.KCPTUN_CRYPT,
            "datashard": 10,
            "mode": Config.KCPTUN_MODE,
            "mtu": 1350,
            "key": str(Config.KCPTUN_KEY),
            "parityshard": 3
        },
        "ServerPort": Config.KCPTUN_LISTEN,
        "Password": str(Config.KCPTUN_KEY),
        "OTA": False,
        "ServerHost": ip
    }
    temp_json = '/tmp/com.qiuyuzhou.ShadowsocksX-NG.json'
    temp_plist = '/tmp/com.qiuyuzhou.ShadowsocksX-NG.plist'
    plist_to_json = ('plutil -convert json ~/Library/Preferences/'
                     'com.qiuyuzhou.ShadowsocksX-NG.plist -o {}')
    plist_to_json = plist_to_json.format(temp_json)
    os.system(plist_to_json)
    with open(temp_json) as f:
        data = json.load(f)
    server_profiles = data.get('ServerProfiles')
    index = 0
    if server_profiles:
        index = len(server_profiles)
        for i, profile in enumerate(server_profiles):
            if profile.get('Remark') == 'Vultr':
                index = i
                data['ServerProfiles'].remove(profile)
    else:
        data['ServerProfiles'] = []
    data['ServerProfiles'].insert(index, new_profile)
    data['ActiveServerProfileId'] = ''
    with open(temp_json, 'wb') as f:
        json.dump(data, f)
    json_to_plist = ('plutil -convert binary1 {} -o {}')
    json_to_plist = json_to_plist.format(temp_json, temp_plist)
    os.system(json_to_plist)
    defaults_import = 'defaults import com.qiuyuzhou.ShadowsocksX-NG {}'
    defaults_import = defaults_import.format(temp_plist)
    os.system(defaults_import)


def restart_shadowsocksx_ng():
    stop = 'ps aux|grep \'[S]hadowsocksX-NG\'|awk \'{print $2}\'|xargs kill -9'
    start = 'open /Applications/ShadowsocksX-NG.app'
    os.system(stop)
    os.system(start)


def main():
    script_name = Config.SCRIPT_NAME
    sshkey_name = Config.SSHKEY_NAME
    script_content = generate_startup_script()
    destroy_duplicated_script(script_name)
    print 'Creating startupscript...'
    scriptid = create_startupscript(script_name, script_content)
    print 'Startupscript created, scriptid: {}.'.format(scriptid)
    sshkeyid = None
    if sshkey_name:
        print 'Fetching sshkeyid of {}...'.format(sshkey_name)
        sshkeyid = get_sshkeyid(sshkey_name)
        print 'SSHKEY ID: {}.'.format(sshkeyid)
    destroy_duplicated_server(Config.LABEL)
    print 'Creating server...'
    subid = create_server(Config.DCID,
                          Config.VPSPLANID,
                          Config.OSID,
                          scriptid,
                          sshkeyid=sshkeyid,
                          hostname=Config.HOSTNAME,
                          label=Config.LABEL)
    print 'Server created, SUBID: {}.'.format(subid)
    power_status = 'running'
    while True:
        info = get_server_info(subid)
        ip = info.get('main_ip')
        if not ip or ip == '0.0.0.0':
            continue
        if power_status != info.get('power_status'):
            power_status = info.get('power_status')
            print 'Status: {}'.format(power_status)
            if power_status == 'running':
                break
    print 'Server main ip: {}.'.format(ip)
    print 'Running ssserver at {}:{}'.format(ip, Config.SSSERVER_PORT)
    print 'Running kcptun server at {}:{}'.format(ip, Config.KCPTUN_LISTEN)
    update_shadowsocksx_ng_profile(ip)
    restart_shadowsocksx_ng()


if __name__ == '__main__':
    main()
