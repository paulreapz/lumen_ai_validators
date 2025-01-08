
# Lumen Validator AI – Advanced Manual

- [Node requirements](#node-requirements)
- [What does it do with your Validator Node exactly](#what-does-it-do-with-your-validator-node-exactly)
  - [Configure Ubuntu](#configure-ubuntu)
  - [Bootstrap Solana cli](#bootstrap-solana-cli)
  - [Configure node monitoring](#configure-node-monitoring)
- [How to install Ansible](#how-to-install-ansible)
  - [on MacOS](#on-macos)
  - [on Ubuntu](#on-ubuntu)
  - [on Windows](#on-windows)
- [How to configure Solana Validator Manager](#how-to-configure-solana-validator-manager)
- [How to use](#how-to-use)
  - [from local machine](#from-local-machine)
  - [directly from Validator Node](#from-validator-node)
  - [via docker](#via-docker)
- [Which functions are supported](#which-functions-are-supported)
  - [install](#install-validator-node)
  - [update Solana Version](#update-solana-version)
  - [install or update monitoring](#install-or-update-monitoring)
    - [how to install monitoring with ansible](#how-to-install-monitoring-with-ansible)
    - [how to install monitoring manually](#how-to-install-monitoring-manually)
  - [migrate your current setup to supported by lumen](#migrate-your-current-setup-to-supported-by-lumen)
    - [how to migrate your setup semi-automatically](#how-to-migrate-your-setup-semi-automatically)
    - [how to migrate your setup manually](#how-to-migrate-your-setup-manually)
      [Useful links](#useful-links)
- [How can you support this project](#how-can-you-support-this-project)
- [History](history.md)
- [Roadmap](roadmap.md)

## Node requirements

* We have tested it only with Ubuntu 20.04, but every linux distro with apt and systemd should be supported.
* Support for other Linux-Distributives will be implemented soon.
* Check Solana [Validator requirements](https://docs.solana.com/running-validator/validator-reqs)

## What does it do with your Validator Node exactly

### Configure Ubuntu

[Ubuntu role](../roles/configure_ubuntu)

that role configures your ubuntu node to be more performant and stable with validation

1. Create ansible user
2. Create solana user
3. Create swap file
4. Create ram disk for accounts db
5. Set cpu governor to performance
6. Configure firewall

### Bootstrap Solana cli

[Solana cli role](../roles/solana_cli)

that role installs or updates solana cli

### Configure node monitoring

- [monitoring](../roles/monitoring)

that role configures sending of validator and node metrics to our [grafana dashboard](https://solana.thevalidators.io)

## How to install Ansible

### On macOS

    brew update; brew install ansible

### On Ubuntu

    apt-get update; apt-get install ansible

### On Windows

unfortunately ansible is not directly supported on Windows, we are working on a docker image
which will directly provide a support for Solana Validator Manager, until that you can use
[ansible docker image](https://hub.docker.com/r/ansible/ansible) on your own.

## How to configure Solana Validator Manager

*!only testnet configuration is supported now!*

1. clone git repository
   git clone ...
1. copy or rename [inventory_example directory](../inventory_example) to directory named *inventory*
2. add to your inventory/hosts.yaml

* validator name
* ip-address of your validator node

```yaml
all:
  children:
    local:
      vars:
        become: false
        ansible_connection: local
        ansible_python_interpreter: "{{ ansible_playbook_python }}"
      hosts:
        localhost
    remote:
      vars:
        ansible_user: root
      children:
        validator:
          vars:
            validator_name: <- HERE
#            keybase_username: ""
#            validator_homepage: ""
            upload_validator_keys: False <- Set it to True if you want to upload your keys
#            secrets_path: /home/solana/.secrets
#            set_validator_info: True
#            service_user: solana
#            ledger_path: /home/solana/ledger
#            lvm_enabled: False
#            lvm_vg: vg00
#            solana_validator_service: restarted <- Set it to stopped if you want to check your setup
#            swap_file_size_gb: 64
#            ramdisk_size_gb: 64
#            cluster_environment: testnet
#            cluster_rpc_address: https://api.testnet.solana.com
          hosts:
            0.0.0.0 <- HERE
```

in case you have already identity keys (the most of you will have at least a validator identity key)

4. copy your validator identity key, if any, into .secrets/{{YOUR VALIDATOR NAME}}/solana
5. copy your vote account identity key, if any, into .secrets/{{YOUR VALIDATOR NAME}}/solana
6. set upload_validator_keys to True

## How to use

### from local machine

1. make sure you have access to you validator node as a root user via [ssh-key](https://www.cyberciti.biz/faq/ubuntu-18-04-setup-ssh-public-key-authentication/)
2. configure hosts.yaml
3. start playbook

ansible-playbook install_validator.yaml -v

if you run an ubuntu server with more or less standard configuration than in few minutes
your validator node should be up, and you can observe your metrics on [our metrics dashboard](https://solana.thevalidators.io)

### from Validator Node

coming soon!

## Which functions are supported

### Install Validator Node

ansible-playbook pb_install_validator.yaml -v

### Update Solana Version

* bump solana version in group_vars/all.yaml

```yaml
...
validator:
  version: v1.6.7 <- set new version here
...
```

* start ansible playbook

  ansible-playbook pb_update_validator.yaml  -v

### Install or update Monitoring

* if you just want to use monitoring
* or want update monitoring library

#### How to install monitoring with ansible

ansible-playbook pb_install_monitoring.yaml  -v

#### How to install monitoring manually

From server command line, user root, paste the whole command and run it:

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/mfactory-lab/lumen/latest/install/install_monitoring.sh)"

### Migrate your current setup to supported by lumen

#### How to migrate your setup semi-automatically

coming soon

#### How to migrate your setup manually

coming soon
