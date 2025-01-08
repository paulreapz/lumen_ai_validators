#!/bin/bash
#set -x -e

update_monitoring() {
  cd
  rm -rf sv_manager/
  if [[ $(grep cluster_environment /etc/sv_manager/sv_manager.conf | cut -d':' -f2) == *"testnet"* ]];
  then
  inventory=testnet
  else
  inventory=mainnet
  fi

  if [[ $(which apt | wc -l) -gt 0 ]]
  then
  pkg_manager=apt
  elif [[ $(which yum | wc -l) -gt 0 ]]
  then
  pkg_manager=yum
  fi

  echo "### Update packages... ###"
  $pkg_manager update
  echo "### Install ansible, curl, unzip... ###"
  $pkg_manager install ansible curl unzip --yes

  echo "### Download Solana validator manager"
  cmd="https://github.com/mfactory-lab/sv-manager/archive/refs/tags/$1.zip"
  echo "starting $cmd"
  curl -fsSL "$cmd" --output sv_manager.zip
  echo "### Unpack Solana validator manager ###"
  unzip ./sv_manager.zip -d .

  mv sv-manager* sv_manager
  rm ./sv_manager.zip
  cd ./sv_manager || exit
  cp -r ./inventory_example ./inventory

  ansible-playbook --connection=local --inventory ./inventory/$inventory.yaml --limit localhost  playbooks/pb_install_monitoring.yaml --tags telegraf.configure,monitoring.script --extra-vars "@/etc/sv_manager/sv_manager.conf"
}

if [ -f /etc/sv_manager/sv_manager.conf ]
then
echo "### Monitoring has been already installed. Start update?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) update_monitoring "${1:-latest}"; break;;
        No ) echo "### Aborting update. No changes are made on the system."; exit;;
    esac
done
else
echo '### Monitoring is not installed, or the version is too old. ###'
echo '### Please run full install of the latest version using this command: ###'
echo '### /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/mfactory-lab/sv-manager/latest/install/install_monitoring.sh)" ###'
fi
