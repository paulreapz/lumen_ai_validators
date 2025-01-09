#!/bin/bash
#set -x -e

# Warning and Information
cat << "EOF"
###################### WARNING!!! ######################
###   This script will install the Solana Sys Tuner  ###
###   for the Solana Validator.                      ###
########################################################
EOF

install_sys_tuner() {

  # Clean previous manager setup
  rm -rf sv_manager/

  # Detect package manager
  if [[ $(which apt | wc -l) -gt 0 ]]; then
    pkg_manager=apt
  elif [[ $(which yum | wc -l) -gt 0 ]]; then
    pkg_manager=yum
  fi

  echo "### Updating packages... ###"
  $pkg_manager update
  echo "### Installing dependencies... ###"
  $pkg_manager install ansible curl unzip --yes

  ansible-galaxy collection install ansible.posix community.general

  echo "### Downloading Solana validator manager ###"
  cmd="https://github.com/mfactory-lab/sv-manager/archive/refs/tags/$sv_manager_version.zip"
  curl -fsSL "$cmd" --output sv_manager.zip
  echo "### Unpacking manager ###"
  unzip ./sv_manager.zip -d .
  mv sv-manager* sv_manager
  rm ./sv_manager.zip
  cd sv_manager || exit 1
  cp -r ./inventory_example ./inventory

  ansible-playbook --connection=local --inventory ./inventory/mainnet.yaml --limit localhost playbooks/pb_install_validator.yaml --tags validator.service.sys-tuner

  echo "### Cleaning up Ansible installation ###"
  $pkg_manager remove ansible --yes

  echo "### Solana Sys Tuner Service installed. Check status with: 'systemctl status solana-sys-tuner' ###"
}

# Default manager version
sv_manager_version=${sv_manager_version:-latest}

# Main script logic
cat << "EOF"
This script will set up the Solana Sys Tuner Service with default parameters. Proceed?
EOF
select yn in "Yes" "No"; do
    case $yn in
        Yes ) install_sys_tuner; break;;
        No ) echo "Aborting installation. No changes made."; exit 0;;
    esac
done
