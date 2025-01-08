#!/bin/bash
#set -x -e

echo "###################### WARNING!!! ######################"
echo "###   This script will install the Solana Sys Tuner  ###"
echo "###   for the Solana Validator.                       ###"
echo "########################################################"

install_validator () {

  rm -rf sv_manager/

  if [[ $(which apt | wc -l) -gt 0 ]]
  then
  pkg_manager=apt
  elif [[ $(which yum | wc -l) -gt 0 ]]
  then
  pkg_manager=yum
  fi

  echo "Updating packages..."
  $pkg_manager update
  echo "Installing ansible, curl, unzip..."
  $pkg_manager install ansible curl unzip --yes

  ansible-galaxy collection install ansible.posix
  ansible-galaxy collection install community.general

  echo "Downloading Solana validator manager version $sv_manager_version"
  cmd="https://github.com/mfactory-lab/sv-manager/archive/refs/tags/$sv_manager_version.zip"
  echo "starting $cmd"
  curl -fsSL "$cmd" --output sv_manager.zip
  echo "Unpacking"
  unzip ./sv_manager.zip -d .

  mv sv-manager* sv_manager
  rm ./sv_manager.zip
  cd ./sv_manager || exit
  cp -r ./inventory_example ./inventory

  # shellcheck disable=SC2154
  #echo "pwd: $(pwd)"
  #ls -lah ./


  ansible-playbook --connection=local --inventory ./inventory/mainnet.yaml --limit localhost  playbooks/pb_install_validator.yaml --tags validator.service.sys-tuner

  echo "### 'Uninstall ansible ###"

  $pkg_manager remove ansible --yes
  
  echo "### Solana Sys Tuner Servie installed. You can check the status with 'systemctl status solana-sys-tuner' ###"


}


while [ $# -gt 0 ]; do

   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare ${param}="$2"
  #      echo $1 $2 // Optional to see the parameter:value result
   fi

  shift
done

sv_manager_version=${sv_manager_version:-latest}

echo "installing sv manager version $sv_manager_version"

echo "This script will setup the Solana Sys Tuner Service with default parameters. Proceed?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) install_validator "$sv_manager_version" "$extra_vars" "$solana_version" "$tags" "$skip_tags"; break;;
        No ) echo "Aborting install. No changes will be made."; exit;;
    esac
done
