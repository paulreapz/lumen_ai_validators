#!/bin/bash
#set -x -e

echo "###################### WARNING!!! ###################################"
echo "###   This script will perform the following operations:          ###"
echo "###   * wait for validator restart window                         ###"
echo "###   * validator binaries                                        ###"
echo "###   * restart sys tuner service                                 ###"
echo "###   * restart validator service                                 ###"
echo "###   * wait for catchup                                          ###"
echo "#####################################################################"

update_validator() {
  sudo -i -u solana solana-install init "$version"
  echo "Version "$version" successfully downloaded"
  systemctl restart solana-sys-tuner  
  if [ ! -f /mnt/solana/ledger/admin.rpc ]
  then
    sudo -i -u solana solana-validator --ledger /mnt/solana/ledger wait-for-restart-window
    systemctl restart solana-validator
  else
    echo "Ledger directory not found. Restart your validator service manually."
  fi

}

catchup_info() {

  while true; do

    sudo -i -u solana solana catchup --our-localhost
    status=$?

    if [ $status -eq 0 ]
    then
      exit 0
    fi

    echo "waiting next 30 seconds for rpc"
    sleep 30

  done

}

version=${1:-latest}

echo "updating to version $version"
update_validator
catchup_info
