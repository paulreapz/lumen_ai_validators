# Lumen AI Validators Manager

X: https://x.com/lumenvalidators
Telegram: https://t.me/lumenvalidators
Website: https://lumenvalidators.ai/
CA: `LumenDrG2aqqHzh7TTdohoGgyDhQjoJRwj4oLwW5mMx`

### Automatically bootstrap a Solana validator node, optimize its performance, and connect the node to a monitoring dashboard

[Solana](https://solana.com/) is a fast, secure, and censorship-resistant blockchain providing open infrastructure necessary for global adoption.

In order to run, the Solana blockchain requires a decentralized network comprising computing resources to validate transactions as well as storage for ledger redundancy.

The computer resources are provided by validators who need to maintain high-performance Linux nodes.

There are now two Solana clusters, [Mainnet-Beta](https://explorer.solana.com/)  and [Testnet](https://explorer.solana.com/?cluster=testnet).

The Mainnet-Beta cluster is maintained by ~700 validators, and the Testnet cluster by ~1700 more validators.

Most of the people running these just bootstrap their nodes manually, referring to the Solana docs or similar community guides. Apparently, there are no 2 identical setups across these 2400 validators.

As a result, it is virtually impossible to support validators having issues with their nodes and/or help them improve their node, thus contributing to the overall cluster performance.

What we would like to do is provide a toolkit to help validators bootstrap and maintain their nodes in a uniform, consistent way.

The Ansible scripts we have created for this purpose are a compilation of best practices and community guidelines.

Please use them, enjoy them, and improve them.

### Quick Install

* Log in to your server
* Create the key pair file (you can also upload it via scp if you prefer):
  ````shell
  nano ~/validator-keypair.json
  ````   
  Paste your key pair, save the file (ctrl-O) and exit (ctrl-X).


  If you have a *vote account* key pair, create the key pair file (or upload it via scp):
  ````shell
   nano ~/vote-account-keypair.json
  ````  
  Paste your key pair, save the file (ctrl-O) and exit (ctrl-X).
* Run this command…

````shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/mfactory-lab/lumen/latest/install/install_validator.sh)"
````
  <img src="docs/launch.gif" width=500>
…and follow the wizard’s instructions (__enter your own Node name!__):

  <img src="docs/wizard.gif" width=500>

That's it, you are all set!

### How to update validator

````shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/mfactory-lab/lumen/latest/install/update_test_validator_version.sh)" --version 1.14.2
````

### how to update monitoring

````shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/mfactory-lab/lumen/latest/install/update_monitoring.sh)" 
````


### If you want more control over the configuration of your node, please refer to the [advanced technical specifications](docs/advanced.md)


## Useful links

* [Solana](https://solana.com/)
* [Monitoring Dashboard](https://solana.thevalidators.io/)
* [Validator docs](https://docs.solana.com/running-validator)
