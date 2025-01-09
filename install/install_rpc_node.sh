#!/bin/bash
#set -x -e

# Warning and Information
cat << "EOF"
###################### WARNING!!! ######################
###   This script will bootstrap an RPC node         ###
###   for the Solana blockchain, and connect         ###
###   it to the monitoring dashboard                 ###
###   at solana.thevalidators.io                     ###
########################################################
EOF

install_rpc() {

  echo "### Select the cluster for RPC node setup ###"
  select cluster in "mainnet-beta" "testnet"; do
      case $cluster in
          mainnet-beta ) inventory="mainnet.yaml"; break;;
          testnet ) inventory="testnet.yaml"; break;;
      esac
  done

  echo "Please enter a name for your RPC node: "
  read VALIDATOR_NAME
  read -e -p "Enter the full path to your validator key pair file (leave blank to create new keys): " -i "" PATH_TO_VALIDATOR_KEYS

  read -e -p "Enter new RAM drive size in GB (recommended: server RAM minus 16GB): " -i "48" RAM_DISK_SIZE
  read -e -p "Enter new server swap size in GB (recommended: equal to server RAM): " -i "64" SWAP_SIZE

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

  extra_vars="{ 'validator_name':'$VALIDATOR_NAME', 'local_secrets_path':'$PATH_TO_VALIDATOR_KEYS', 'swap_file_size_gb':$SWAP_SIZE, 'ramdisk_size_gb':$RAM_DISK_SIZE, 'fail_if_no_validator_keypair': False }"

  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit localhost_rpc playbooks/pb_config.yaml --extra-vars "$extra_vars"

  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit localhost_rpc playbooks/pb_install_validator.yaml --extra-vars "/etc/sv_manager/sv_manager.conf"

  echo "### Cleaning up Ansible installation ###"
  $pkg_manager remove ansible --yes

  echo "### RPC node setup complete. Monitor at: https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring?&var-server=$VALIDATOR_NAME ###"
}

# Default manager version
sv_manager_version=${sv_manager_version:-latest}

# Main script logic
cat << "EOF"
This script will bootstrap a Solana RPC node. Proceed?
EOF
select yn in "Yes" "No"; do
    case $yn in
        Yes ) install_rpc; break;;
        No ) echo "Aborting installation. No changes made."; exit 0;;
    esac
done
