#!/bin/bash

CONF=$1

echo $CONF


cp $CONF /etc/wireguard/
chown root:root /etc/wireguard/$CONF
chmod 600 /etc/wireguard/$CONF

systemctl enable wg-quick@$CONF
systemctl start wg-quick@$CONF
wg show

exit 0
