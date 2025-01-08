#!/bin/bash
#set -x -e


update_solana_version() {
  sudo -i -u solana solana-install init 1.7.12
}

create_snapshot_form_ledger() {
  sudo -i -u solana solana-ledger-tool --ledger /mnt/ledger create-snapshot 95038710 /mnt/ledger/shapshots/  --snapshot-archive-path /mnt/ledger/shapshots/ --hard-fork 95038710 --wal-recovery-mode skip_any_corrupted_record
}

create_config() {

  echo "### Update packages... ###"
  apt update
  echo "### Install ansible, curl, unzip... ###"
  apt install ansible curl unzip --yes

  ansible-galaxy collection install ansible.posix
  ansible-galaxy collection install community.general

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

  echo "### Which cluster do you want to configure? ###"
  select cluster in "mainnet-beta" "testnet"; do
      case $cluster in
          mainnet-beta ) cluster_environment="mainnet-beta"; break;;
          testnet ) cluster_environment="testnet"; break;;
      esac
  done


  echo "### Please type your validator name: "
  read VALIDATOR_NAME
  echo "### Please type the full path to your validator keys: "
  read PATH_TO_VALIDATOR_KEYS

  if [ ! -f "$PATH_TO_VALIDATOR_KEYS/validator-keypair.json" ]
  then
    echo "key $PATH_TO_VALIDATOR_KEYS/validator-keypair.json not found. Pleas verify and run the script again"
    exit
  fi

  read -e -p "### Please tell which user is running validator: " SOLANA_USER

  ansible-playbook --connection=local --inventory ./inventory --limit local  playbooks/pb_config.yaml --extra-vars "{'host_hosts': 'local', \
  'solana_user': '$SOLANA_USER', \
  'validator_name':'$VALIDATOR_NAME', \
  'secrets_path': '$PATH_TO_VALIDATOR_KEYS', \
  'flat_path': 'True', \
  'cluster_environment':'$cluster_environment'\
  }"

  remove ansible --yes

}

update_validator() {

  rm -rf sv_manager/

  echo "### Update packages... ###"
  apt update
  echo "### Install ansible, curl, unzip... ###"
  apt install ansible curl unzip --yes

  ansible-galaxy collection install ansible.posix
  ansible-galaxy collection install community.general

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

  ansible-playbook --connection=local --inventory ./inventory --limit local  playbooks/pb_cluster_restart.yaml --extra-vars "@/etc/sv_manager/sv_manager.conf" --extra-vars 'host_hosts=local'


  apt remove ansible --yes

  systemctl daemon-reload
  systemctl restart solana-validator
}

process() {
  update_solana_version
  create_snapshot_form_ledger
  update_validator "${1:-latest}" "${2:-""}"
}

if [ -f /etc/sv_manager/sv_manager.conf ]
then
echo "### Validator has been already installed. Start update?"
  select yn in "Yes" "No"; do
      case $yn in
          Yes ) update_validator "${1:-latest}" "${2:-""}"; break;;
          No ) echo "### Aborting update. No changes are made on the system."; exit;;
      esac
  done
else
  echo '### Validator is not installed, or the version is too old. ###'
  echo '### should we create valiadtor config. ###'
  select yn in "Yes" "No"; do
      case $yn in
          Yes ) create_config "${1:-latest}"; break;;
          No ) echo "### Aborting update. No changes are made on the system."; exit;;
      esac
  done

fi
