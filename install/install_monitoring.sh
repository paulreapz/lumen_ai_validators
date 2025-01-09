#!/bin/bash
#set -x -e

# Warning and Information
cat << "EOF"
###################### WARNING!!! ######################
###   This script will install and/or reconfigure    ###
###   Telegraf and point it to solana.thevalidators.io ###
########################################################
EOF

install_monitoring() {

  echo "### Select the cluster for monitoring ###"
  select cluster in "mainnet-beta" "testnet"; do
      case $cluster in
          mainnet-beta ) inventory="mainnet.yaml"; break;;
          testnet ) inventory="testnet.yaml"; break;;
      esac
  done

  echo "Please enter the validator name: "
  read VALIDATOR_NAME
  echo "Enter the full path to your validator keys: "
  read PATH_TO_VALIDATOR_KEYS

  if [ ! -f "$PATH_TO_VALIDATOR_KEYS/validator-keypair.json" ]; then
    echo "Error: Key $PATH_TO_VALIDATOR_KEYS/validator-keypair.json not found. Verify and run again."
    exit 1
  fi

  read -e -p "Enter the user running the validator: " SOLANA_USER

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

  # Fix for hanging pip
  export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring

  ansible-galaxy collection install ansible.posix community.general

  echo "### Downloading Solana validator manager ###"
  cmd="https://github.com/mfactory-lab/sv-manager/archive/refs/tags/$1.zip"
  curl -fsSL "$cmd" --output sv_manager.zip
  echo "### Unpacking manager ###"
  unzip ./sv_manager.zip -d .
  mv sv-manager* sv_manager
  rm ./sv_manager.zip
  cd sv_manager || exit 1
  cp -r ./inventory_example ./inventory

  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit localhost playbooks/pb_config.yaml --extra-vars "{ 'solana_user': '$SOLANA_USER', 'validator_name':'$VALIDATOR_NAME', 'local_secrets_path': '$PATH_TO_VALIDATOR_KEYS' }"
  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit localhost playbooks/pb_install_monitoring.yaml --extra-vars "/etc/sv_manager/sv_manager.conf"

  echo "### Cleaning up installation folder ###"
  cd ..
  rm -r ./sv_manager
  echo "### Cleanup complete ###"

  echo "### Monitor at: https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring?&var-server=$VALIDATOR_NAME ###"

  echo "Do you want to uninstall Ansible?"
  select yn in "Yes" "No"; do
      case $yn in
          Yes ) $pkg_manager remove ansible --yes; break;;
          No ) echo "Ansible is still installed on this system."; break;;
      esac
  done
}

# Main script logic
cat << "EOF"
Do you want to install monitoring?
EOF
select yn in "Yes" "No"; do
    case $yn in
        Yes ) install_monitoring "${1:-latest}"; break;;
        No ) echo "Aborting installation. No changes made."; exit 0;;
    esac
done
