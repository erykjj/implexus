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


def create_deploy_script(name):
    return f'#!/bin/bash\n\ncp {name}.conf /etc/wireguard/\nchown root:root /etc/wireguard/{name}.conf\nchmod 600 /etc/wireguard/{name}.conf\n\nsystemctl enable wg-quick@{name}\nsystemctl start wg-quick@{name}\n\nwg show {name}\n\nexit 0'


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
        conf = f"[Interface]\n# Name: {device}\nAddress = {mesh[device]['Address']}/24\nPrivateKey = {mesh[device]['PrivateKey']}"
        if 'ListenPort' in mesh[device].keys():
            conf += f"\nListenPort = {mesh[device]['ListenPort']}"
        for peer in mesh.keys():
            if peer == 'NetworkName' or peer == device:
                continue
            if 'Endpoint' not in mesh[peer].keys() and 'AllowedIPs' not in mesh[device].keys():
                continue
            conf += f"\n\n[Peer]\n# Name: {peer}\nPublicKey = {mesh[peer]['PublicKey']}"
            if 'Endpoint' in mesh[peer].keys():
                conf += f"\nEndpoint = {mesh[peer]['Endpoint']}:{mesh[peer]['ListenPort']}"
            conf += f"\nAllowedIPs = {mesh[peer]['Address']}/32"
            if 'AllowedIPs' in mesh[peer].keys():
                conf += f", {mesh[peer]['AllowedIPs']}"
            if 'PersistentKeepalive' in mesh[device].keys():
                conf += f"\nPersistentKeepalive = {mesh[device]['PersistentKeepalive']}"

        file_dir = f"{output_dir}/{device}/"
        with open(file_dir + f"{mesh['NetworkName']}.conf", 'w', encoding='UTF-8') as f:
            f.write(conf)
        with open(file_dir + f"deploy_{device}.sh", 'w', encoding='UTF-8') as f:
            f.write(create_deploy_script(mesh['NetworkName']))
        print(f'Generated config and deploy script for {device}')
    # with open(f"{output_dir}/{mesh['NetworkName']}.yaml", 'w', encoding='UTF-8') as f:
    #     yaml.dump(mesh, f, Dumper=yaml.dumper.SafeDumper, indent=4)


# PROJECT_PATH = Path(__file__).resolve().parent
# APP = Path(__file__).stem

OUTPUT_DIR = '/mnt/ramdisk'
process_config('config.yaml')

