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

VERSION = 'v0.0.1'


import argparse, yaml, os, subprocess
# from pathlib import Path
from pprint import pprint

def sh(command, arguments='', inp=''):
    res = subprocess.run([command, arguments], stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=inp.encode('utf-8'))
    if res.stderr.decode('utf-8'):
        print(res.stderr.decode('utf-8'))
        exit()
    return res.stdout.decode('utf-8')

def read_yaml(config):
    with open(config) as f:
        data = yaml.load(f, Loader=yaml.loader.SafeLoader)
    mesh = {}
    mesh['Network'] = {
        'Name': data['mesh']['name'],
        # 'Range': data['mesh']['ip_range'],
        'PersistentKeepalive': data['mesh']['keep_alive'] }
    for device in data['devices']:
        private_key = sh('wg', 'genkey').rstrip('\n')
        public_key = sh('wg', 'pubkey', private_key).rstrip('\n')
        mesh[device['name']] = {
            'Address': device['mesh_ip'],
            'PrivateKey': private_key,
            'PublicKey': public_key }
        if 'real_ip' in device.keys():
            mesh[device['name']]['Endpoint'] = device['real_ip']
        if 'port' in device.keys():
            mesh[device['name']]['ListenPort'] = device['port']
        if 'connect_to' in device.keys():
            mesh[device['name']]['Peers'] = device['connect_to']
    return mesh

def output_configs(mesh):
    output_dir = OUTPUT_DIR + '/' + mesh['Network']['Name']
    os.makedirs(output_dir, exist_ok=True)
    for device in mesh:
        if device == 'Network':
            continue
        os.makedirs(output_dir + '/' + device, exist_ok=True)
        conf = f"[Interface]\n# Name: {device}\nAddress = {mesh[device]['Address']}/24\nPrivateKey = {mesh[device]['PrivateKey']}"
        if 'ListenPort' in mesh[device].keys():
            conf += f"\nListenPort = {mesh[device]['ListenPort']}"
        if 'Peers' in mesh[device].keys():
            for peer in mesh[device]['Peers']:
                conf += f"\n\n[Peer]\n# Name: {peer}\nPublicKey = {mesh[peer]['PublicKey']}\nEndpoint = {mesh[peer]['Endpoint']}"
                if 'ListenPort' in mesh[peer].keys():
                    conf += f":{mesh[peer]['ListenPort']}"
                conf += f"\nAllowedIPs = {mesh[peer]['Address']}\nPersistentKeepalive = {mesh['Network']['PersistentKeepalive']}"
        file_name = f"{output_dir}/{device}/wg-{mesh['Network']['Name']}.conf"
        with open(f"{output_dir}/{device}/wg-{mesh['Network']['Name']}.conf", 'w', encoding='UTF-8') as f:
            f.write(conf)
        print(f'Generated {file_name}')

# if __name__ == "__main__":
    # PROJECT_PATH = Path(__file__).resolve().parent
    # APP = Path(__file__).stem

OUTPUT_DIR = '/mnt/ramdisk'
mesh = read_yaml('network.yaml')
output_configs(mesh)
