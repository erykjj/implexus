#!/usr/bin/env python3

"""
  File:           implexus

  Description:    Generate and manage Wireguard mesh networks

  MIT License:    Copyright (c) 2023 Eryk J.

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
"""

VERSION = 'v0.0.3'


import argparse, os, subprocess, yaml
# from pathlib import Path
from pprint import pprint


def sh(command, arguments='', inp=''):
    res = subprocess.run([command, arguments], stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=inp.encode('utf-8'))
    if res.stderr.decode('utf-8'):
        print(res.stderr.decode('utf-8'))
        exit()
    return res.stdout.decode('utf-8')


def create_deploy_script(name, port):
    if port:
        note = f'echo "You may need to add a rule to your firewall to allow traffic to the WireGuard interface\'s port:"\necho "sudo uwf allow {port}/udp"\necho "sudo ufw reload"\n\n'
    else:
        note = ''
    return f'#!/bin/bash\n\nsystemctl stop wg-quick@{name}\nsystemctl disable wg-quick@{name}\n\ncp {name}.conf /etc/wireguard/\nchown root:root /etc/wireguard/{name}.conf\nchmod 600 /etc/wireguard/{name}.conf\n\nsystemctl enable wg-quick@{name}\nsystemctl start wg-quick@{name}\n\nwg show {name}\n\n{note}exit 0'


def process_config(config):
    with open(config) as f:
        mesh = yaml.load(f, Loader=yaml.loader.SafeLoader)

    output_dir = OUTPUT_DIR + '/' + mesh['NetworkName']
    os.makedirs(output_dir, exist_ok=True)

    for device in mesh.keys():
        if device == 'NetworkName':
            continue
        os.makedirs(output_dir + '/' + device, exist_ok=True)
        if 'PrivateKey' not in mesh[device].keys():
            mesh[device]['PrivateKey'] = sh('wg', 'genkey').rstrip('\n')
            mesh[device]['PublicKey'] = sh('wg', 'pubkey', mesh[device]['PrivateKey']).rstrip('\n')

    for device in mesh.keys():
        if device == 'NetworkName':
            continue
        if 'AllowedIPs' in mesh[device].keys():
            subnet = '/24'
            routing = f"\n\n# IP forwarding\nPreUp = sysctl -w net.ipv4.ip_forward=1\n\n# IP masquerading\nPreUp = iptables -t mangle -A PREROUTING -i {mesh['NetworkName']} -j MARK --set-mark 0x30\nPreUp = iptables -t nat -A POSTROUTING ! -o {mesh['NetworkName']} -m mark --mark 0x30 -j MASQUERADE\nPostDown = iptables -t mangle -D PREROUTING -i {mesh['NetworkName']} -j MARK --set-mark 0x30\nPostDown = iptables -t nat -D POSTROUTING ! -o {mesh['NetworkName']} -m mark --mark 0x30 -j MASQUERADE"
        else:
            subnet = '/32'
            routing = ''
        conf = f"[Interface]\n# Name: {device}\nAddress = {mesh[device]['Address']}{subnet}\nPrivateKey = {mesh[device]['PrivateKey']}"
        if 'ListenPort' in mesh[device].keys():
            conf += f"\nListenPort = {mesh[device]['ListenPort']}{routing}"
        else:
            mesh[device]['ListenPort'] = False
        for peer in mesh.keys():
            if peer == 'NetworkName' or peer == device:
                continue
            if 'Endpoint' not in mesh[peer].keys() and 'AllowedIPs' not in mesh[device].keys():
                continue
            conf += f"\n\n[Peer]\n# Name: {peer}\nPublicKey = {mesh[peer]['PublicKey']}"
            if 'Endpoint' in mesh[peer].keys():
                conf += f"\nEndpoint = {mesh[peer]['Endpoint']}:{mesh[peer]['ListenPort']}"

            if 'AllowedIPs' in mesh[peer].keys():
                conf += f", {mesh[peer]['AllowedIPs']}"
            else:
                conf += f"\nAllowedIPs = {mesh[peer]['Address']}/32"
            if 'PersistentKeepalive' in mesh[device].keys():
                conf += f"\nPersistentKeepalive = {mesh[device]['PersistentKeepalive']}"

        file_dir = f"{output_dir}/{device}/"
        with open(f"{file_dir}{mesh['NetworkName']}.conf", 'w', encoding='UTF-8') as f:
            f.write(conf)
            os.chmod(f"{file_dir}{mesh['NetworkName']}.conf", mode=0o600)
        with open(file_dir + f"deploy_{device}.sh", 'w', encoding='UTF-8') as f:
            f.write(create_deploy_script(mesh['NetworkName'], mesh[device]['ListenPort']))
            os.chmod(f'{file_dir}deploy_{device}.sh', mode=0o740)
        print(f'Generated config and deploy script for {device}')
    # with open(f"{output_dir}/{mesh['NetworkName']}.yaml", 'w', encoding='UTF-8') as f:
    #     yaml.dump(mesh, f, Dumper=yaml.dumper.SafeDumper, indent=4)


# PROJECT_PATH = Path(__file__).resolve().parent
# APP = Path(__file__).stem

OUTPUT_DIR = '/mnt/ramdisk'
process_config('config.yaml')

