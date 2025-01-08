#!/bin/bash
#set -x -e

echo "###################### WARNING!!! ######################"
echo "###   This script will bootstrap an RPC node         ###"
echo "###   for the Solana blockchain, and connect         ###"
echo "###   it to the monitoring dashboard                 ###"
echo "###   at solana.thevalidators.io                     ###"
echo "########################################################"

install_rpc () {

  echo "### Please choose the cluster: ###"
  select cluster in "mainnet-beta" "testnet"; do
      case $cluster in
          mainnet-beta ) inventory="mainnet.yaml"; break;;
          testnet ) inventory="testnet.yaml"; break;;
      esac
  done

  echo "Please enter a name for your RPC node: "
  read VALIDATOR_NAME
  read -e -p "Please enter the full path to your validator key pair file or leave it blank, then the keys will be created: " -i "" PATH_TO_VALIDATOR_KEYS


  read -e -p "Enter new RAM drive size, GB (recommended size: server RAM minus 16GB):" -i "48" RAM_DISK_SIZE
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

  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit localhost_rpc  playbooks/pb_config.yaml --extra-vars "{ \
  'validator_name':'$VALIDATOR_NAME', \
  'local_secrets_path': '$PATH_TO_VALIDATOR_KEYS', \
  'swap_file_size_gb': $SWAP_SIZE, \
  'ramdisk_size_gb': $RAM_DISK_SIZE, \
  'fail_if_no_validator_keypair: False'
  }"

  if [ ! -z $solana_version ]
  then
    SOLANA_VERSION="--extra-vars {\"solana_version\":\"$solana_version\"}"
  fi
  if [ ! -z $extra_vars ]
  then
    EXTRA_INSTALL_VARS="--extra-vars {$extra_vars}"
  fi
  if [ ! -z $tags ]
  then
    TAGS="--tags {$tags}"
  fi

  ansible-playbook --connection=local --inventory ./inventory/$inventory --limit localhost_rpc  playbooks/pb_install_validator.yaml --extra-vars "@/etc/sv_manager/sv_manager.conf" $SOLANA_VERSION $EXTRA_INSTALL_VARS $TAGS

  echo "### 'Uninstall ansible ###"

  $pkg_manager remove ansible --yes

  echo "### Check your dashboard: https://solana.thevalidators.io/d/e-8yEOXMwerfwe/solana-monitoring?&var-server=$VALIDATOR_NAME"

}


while [ $# -gt 0 ]; do

   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare ${param}="$2"
        #echo $1 $2 // Optional to see the parameter:value result
   fi

  shift
done

sv_manager_version=${sv_manager_version:-latest}

echo "installing sv manager version $sv_manager_version"

echo "This script will bootstrap a Solana RPC node. Proceed?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) install_rpc "$sv_manager_version" "$extra_vars" "$solana_version" "$tags"; break;;
        No ) echo "Aborting install. No changes will be made."; exit;;
    esac
done
