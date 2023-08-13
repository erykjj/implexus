# implexus


## Purpose

This is a Python script to automate the generation of interface configs for multi-peer (WireGuard)[https://www.wireguard.com/] mesh networks. The peers are all listed in an 'outline' (config file in YAML format) passed to the script. See the (sample_config.yaml)[https://github.com/erykjj/implexus/blob/main/sample_config.yaml) for format layout. The `NetworkName` will end up being the network interface name. The `Address` IPs are according to your chosen virtual 'LAN'. You can have multiple mesh networks spanning the same or different devices, as long as the names and IP ranges don't conflict.

Only specify `Endpoint` and `ListenPort` for peers that have a fixed public IP (even via dynamic DNS) and port (via NAT port forwarding). You need at least one such peer to act as a hub (= relay/bouncer), in which case also indicate `AllowedIPs` for that peer with the `/24` suffix, which will make it accept packets destined to the whole subnet. Only have one such peer per network (= interface), though you don't need one at all. You *can* have only point-to-point connections: as long as a peer has a public IP and port, all the others should be able to connect to it, but won't be able to connect to other 'dynamic' peers without a hub/router/relay/bouncer.

The script requires the WireGuard `wg` binary to generate the private/public key-pairs for each device regenerated on each execution - so do it right before deploying to all your device ;-). The script has only been tested under Linux. It will output the *interface.conf* file for each device/peer, as well as a couple of bash scripts: one for automating the install/deploy of the device; the other for removing it. All that needs to be done is to copy the files to the corresponding peer/device and to execute (**as root**) the *deploy_device.sh* script - again, only under Linux, and requires `systemd`. If your device is running a different OS, import the corresponding *interface.conf* file into your WireGuard client.

As the deploy script indicates, you may also have to tweak your firewall to allow the UDP connections to get through to your device.

____
## Installation

Download [latest source](https://github.com/erykjj/implexus/releases/latest) and `python3 -m pip install implexus-*.tar.gz`.

____
## Command-line usage
```
usage: implexus.py [-h] [-v] [-o directory] Outline

Generate WireGuard configs based on a network outline

positional arguments:
  Outline        Network outline (YAML format)

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
  -o directory   Output directory (working dir if not provided)
```

____
## Feedback

Feel free to [get in touch and post any issues and suggestions](https://github.com/erykjj/implexus/issues).

[![RSS of releases](res/rss-36.png)](https://github.com/erykjj/implexus/releases.atom)
