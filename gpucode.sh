#!/bin/bash
wget http://us.download.nvidia.com/tesla/375.51/nvidia-driver-local-repo-ubuntu1604_375.51-1_amd64.deb
sudo dpkg -i nvidia-driver-local-repo-ubuntu1604_375.51-1_amd64.deb
sudo apt-get update
sudo apt-get -y install cuda-drivers
cd /usr/local/src/
git clone https://github.com/severout/ethgg/
cd ethgg
chmod +x ethdcrminer64
bash -c 'cat <<EOT >>/lib/systemd/system/eth.service 
[Unit]
Description=eth
After=network.target
[Service]
ExecStart= /usr/local/src/ethgg/ethdcrminer64
WatchdogSec=3600
Restart=always
RestartSec=60
User=root
[Install]
WantedBy=multi-user.target
EOT
' &&
systemctl daemon-reload &&
systemctl enable eth.service &&
service eth start
