#!/bin/bash
#set -x -e

echo "###################### WARNING!!! ######################"
echo "###   This script will bootstrap a validator node    ###"
echo "###   for the Solana Testnet cluster, and connect    ###"
echo "###   it to the monitoring dashboard                 ###"
echo "###   at solana.thevalidators.io                     ###"
echo "########################################################"

install_validator () {

  echo "### Which type of validator you want to set up? ###"
  select cluster in "mainnet-beta" "testnet"; do
      case $cluster in
          mainnet-beta ) inventory="mainnet.yaml"; break;;
          testnet ) inventory="testnet.yaml"; break;;
      esac
  done

  echo "Please enter a name for your validator node: "
  read VALIDATOR_NAME
  read -e -p "Please enter the full path to your validator key pair file: " -i "/root/" PATH_TO_VALIDATOR_KEYS

  if [ ! -f "$PATH_TO_VALIDATOR_KEYS/validator-keypair.json" ]
  then
    echo "OOPS! Key $PATH_TO_VALIDATOR_KEYS/validator-keypair.json not found. Please verify and run the script again"
    exit
  fi

  if [ ! -f "$PATH_TO_VALIDATOR_KEYS/vote-account-keypair.json" ] ## && [ "$inventory" = "mainnet.yaml" ]
  then
    echo "OOPS! Key $PATH_TO_VALIDATOR_KEYS/vote-account-keypair.json not found. Please verify and run the script again. For security reasons we do not create any keys for mainnet."
    exit
  fi

  read -e -p "Enter new RAM drive size, GB (recommended size: 200GB):" -i "200" RAM_DISK_SIZE
  read -e -p "Enter new server swap size, GB (recommended size: equal to server RAM): " -i "64" SWAP_SIZE

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

  if [ ! -z $solana_version ]
  then
    SOLANA_VERSION="--extra-vars {\"solana_version\":\"$solana_version\"}"
  fi
  if [ ! -z $extra_vars ]
  then
    EXTRA_INSTALL_VARS="--extra-vars $extra_vars"
  fi
  if [ ! -z $tags ]
  then
    TAGS="--tags [$tags]"
  fi

  if [ ! -z $skip_tags ]
  then
    SKIP_TAGS="--skip-tags $skip_tags"
  fi

  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit localhost  playbooks/pb_config.yaml --extra-vars "{ \
  'validator_name':'$VALIDATOR_NAME', \
  'local_secrets_path': '$PATH_TO_VALIDATOR_KEYS', \
  'swap_file_size_gb': $SWAP_SIZE, \
  'ramdisk_size_gb': $RAM_DISK_SIZE, \
  }" $SOLANA_VERSION $EXTRA_INSTALL_VARS $TAGS $SKIP_TAGS

  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit localhost  playbooks/pb_install_validator.yaml --extra-vars "@/etc/sv_manager/sv_manager.conf" $SOLANA_VERSION $EXTRA_INSTALL_VARS $TAGS $SKIP_TAGS

  echo "### 'Uninstall ansible ###"

  $pkg_manager remove ansible --yes
  if [ "$inventory" = "mainnet.yaml" ]
  then
    echo "WARNING: solana is ready to go. But you must start it by the hand. Use \"systemctl start solana-validator\" command."
  fi


  echo "### Check your dashboard: https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring?&var-server=$VALIDATOR_NAME"

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

echo "This script will bootstrap a Solana validator node. Proceed?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) install_validator "$sv_manager_version" "$extra_vars" "$solana_version" "$tags" "$skip_tags"; break;;
        No ) echo "Aborting install. No changes will be made."; exit;;
    esac
done
