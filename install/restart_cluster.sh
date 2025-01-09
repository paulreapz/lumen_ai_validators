#!/bin/bash
#set -x -e

# Warning and Information
cat << "EOF"
###################### WARNING!!! ######################
###   This script will restart the Solana cluster   ###
###   with updates to binaries and configurations.  ###
########################################################
EOF

update_solana_version() {
  echo "### Updating Solana version to 1.7.12 ###"
  sudo -i -u solana solana-install init 1.7.12
}

create_snapshot_from_ledger() {
  echo "### Creating snapshot from ledger ###"
  sudo -i -u solana solana-ledger-tool \
    --ledger /mnt/ledger create-snapshot 95038710 /mnt/ledger/snapshots/ \
    --snapshot-archive-path /mnt/ledger/snapshots/ \
    --hard-fork 95038710 \
    --wal-recovery-mode skip_any_corrupted_record
}

create_config() {
  echo "### Updating packages and installing dependencies ###"
  apt update
  apt install ansible curl unzip --yes

  ansible-galaxy collection install ansible.posix
  ansible-galaxy collection install community.general

  echo "### Downloading Solana validator manager ###"
  cmd="https://github.com/mfactory-lab/sv-manager/archive/refs/tags/$1.zip"
  curl -fsSL "$cmd" --output sv_manager.zip

  echo "### Unpacking manager ###"
  unzip ./sv_manager.zip -d .
  mv sv-manager* sv_manager
  rm ./sv_manager.zip
  cd ./sv_manager || exit
  cp -r ./inventory_example ./inventory

  echo "### Configuring the cluster ###"
  select cluster in "mainnet-beta" "testnet"; do
      case $cluster in
          mainnet-beta ) cluster_environment="mainnet-beta"; break;;
          testnet ) cluster_environment="testnet"; break;;
      esac
  done

  echo "### Enter your validator name: "
  read VALIDATOR_NAME
  echo "### Enter the full path to your validator keys: "
  read PATH_TO_VALIDATOR_KEYS

  if [ ! -f "$PATH_TO_VALIDATOR_KEYS/validator-keypair.json" ]; then
    echo "Key $PATH_TO_VALIDATOR_KEYS/validator-keypair.json not found. Exiting."
    exit 1
  fi

  read -e -p "Enter the user running validator: " SOLANA_USER

  ansible-playbook --connection=local --inventory ./inventory --limit local \
    playbooks/pb_config.yaml --extra-vars "{
    'host_hosts': 'local',
    'solana_user': '$SOLANA_USER',
    'validator_name':'$VALIDATOR_NAME',
    'secrets_path': '$PATH_TO_VALIDATOR_KEYS',
    'flat_path': 'True',
    'cluster_environment':'$cluster_environment'
    }"

  apt remove ansible --yes
}

update_validator() {
  echo "### Removing old manager ###"
  rm -rf sv_manager/

  echo "### Updating packages ###"
  apt update
  apt install ansible curl unzip --yes

  ansible-galaxy collection install ansible.posix
  ansible-galaxy collection install community.general

  echo "### Downloading Solana validator manager ###"
  cmd="https://github.com/mfactory-lab/sv-manager/archive/refs/tags/$1.zip"
  curl -fsSL "$cmd" --output sv_manager.zip
  unzip ./sv_manager.zip -d .
  mv sv-manager* sv_manager
  rm ./sv_manager.zip
  cd ./sv_manager || exit
  cp -r ./inventory_example ./inventory

  echo "### Running cluster restart playbook ###"
  ansible-playbook --connection=local --inventory ./inventory --limit local \
    playbooks/pb_cluster_restart.yaml --extra-vars "@/etc/sv_manager/sv_manager.conf" \
    --extra-vars 'host_hosts=local'

  apt remove ansible --yes

  echo "### Reloading system services ###"
  systemctl daemon-reload
  systemctl restart solana-validator
}

process() {
  update_solana_version
  create_snapshot_from_ledger
  update_validator "${1:-latest}"
}

if [ -f /etc/sv_manager/sv_manager.conf ]; then
  echo "### Validator already installed. Start update? ###"
  select yn in "Yes" "No"; do
      case $yn in
          Yes ) update_validator "${1:-latest}"; break;;
          No ) echo "Aborting update."; exit 0;;
      esac
  done
else
  echo "### Validator not installed or outdated. Create new config? ###"
  select yn in "Yes" "No"; do
      case $yn in
          Yes ) create_config "${1:-latest}"; break;;
          No ) echo "Aborting configuration."; exit 0;;
      esac
  done
fi
