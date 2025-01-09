#!/bin/bash
#set -x -e

# Warning and Information
cat << "EOF"
###################### WARNING!!! ######################
###   This script will bootstrap a validator node    ###
###   for the Solana Testnet cluster, and connect    ###
###   it to the monitoring dashboard                 ###
###   at solana.thevalidators.io                     ###
########################################################
EOF

# Function to install the validator
install_validator() {

  echo "### Select the cluster for setup ###"
  select cluster in "mainnet-beta" "testnet"; do
      case $cluster in
          mainnet-beta ) inventory="mainnet.yaml"; break;;
          testnet ) inventory="testnet.yaml"; break;;
      esac
  done

  echo "Please enter a name for your validator node: "
  read VALIDATOR_NAME
  read -e -p "Enter the full path to your validator key pair file: " -i "/root/" PATH_TO_VALIDATOR_KEYS

  if [ ! -f "$PATH_TO_VALIDATOR_KEYS/validator-keypair.json" ]; then
    echo "Error: Key $PATH_TO_VALIDATOR_KEYS/validator-keypair.json not found. Verify and run again."
    exit 1
  fi

  if [ ! -f "$PATH_TO_VALIDATOR_KEYS/vote-account-keypair.json" ]; then
    echo "Error: Key $PATH_TO_VALIDATOR_KEYS/vote-account-keypair.json not found. Verify and run again."
    exit 1
  fi

  read -e -p "Enter new RAM drive size in GB (default: 200): " -i "200" RAM_DISK_SIZE
  read -e -p "Enter new swap size in GB (default: 64): " -i "64" SWAP_SIZE

  # Clean previous manager setup
  rm -rf sv_manager/

  # Detect package manager
  if [[ $(which apt | wc -l) -gt 0 ]]; then
    pkg_manager=apt
  elif [[ $(which yum | wc -l) -gt 0 ]]; then
    pkg_manager=yum
  fi

  echo "Updating packages..."
  $pkg_manager update
  echo "Installing dependencies..."
  $pkg_manager install ansible curl unzip --yes

  ansible-galaxy collection install ansible.posix community.general

  echo "Downloading Solana validator manager..."
  cmd="https://github.com/mfactory-lab/sv-manager/archive/refs/tags/$sv_manager_version.zip"
  curl -fsSL "$cmd" --output sv_manager.zip

  echo "Unpacking..."
  unzip ./sv_manager.zip -d .
  mv sv-manager* sv_manager
  rm ./sv_manager.zip
  cd sv_manager || exit 1
  cp -r ./inventory_example ./inventory

  extra_vars="{ 'validator_name':'$VALIDATOR_NAME', 'local_secrets_path':'$PATH_TO_VALIDATOR_KEYS', 'swap_file_size_gb':$SWAP_SIZE, 'ramdisk_size_gb':$RAM_DISK_SIZE }"

  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit localhost playbooks/pb_config.yaml --extra-vars "$extra_vars"
  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit localhost playbooks/pb_install_agave_validator.yaml --extra-vars "/etc/sv_manager/sv_manager.conf"

  echo "### Cleanup ansible installation ###"
  $pkg_manager remove ansible --yes

  echo "### Validator setup complete. Monitor at: https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring?&var-server=$VALIDATOR_NAME ###"
}

# Default manager version
sv_manager_version=${sv_manager_version:-latest}

# Main script logic
cat << "EOF"
This script will bootstrap a Solana validator node. Proceed?
EOF
select yn in "Yes" "No"; do
    case $yn in
        Yes ) install_validator; break;;
        No ) echo "Aborting installation. No changes made."; exit 0;;
    esac
done
