# Python prototype for Solana MetaMask proxy

Built on https://github.com/abhinavsingh/proxy.py.git

Requirements (for Ubuntu 18.04):
- python3
- python3-venv
- python3-dev
- gcc

To run internal implementation for Ethereum tokens, start the proxy with:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 -m proxy --hostname 127.0.0.1 --port 9090 --enable-web-server --plugins proxy.plugin.NeonRpcApiPlugin --num-workers=1
```

Then add network `http://localhost:9090/solana` into MetaMask


The repository contains sources for several services with similar logic: 
- proxy
- indexer
- airdropper

Airdropper is a service that analyzes transactions with NeonEVM instructions and looks for liquidity transfers into Neon accounts. The service rewards users that make such transfers with NEON tokens.

The service is configured via environment variables. Further to the common proxy environment, the service accepts the following variables:

- FAUCET_URL 

 > URL to the faucet service for distributing NEON tokens to the users

- INDEXER_ERC20_WRAPPER_WHITELIST 

 > A comma-separated list of ERC20ForSpl wrapped tokens for transfer (those transactions which trigger the service to reward the users). The airdropper looks for the first transfers of such tokens from Solana to Neon (those transfers that lead to the creation of Neon accounts). Alt: provide the `ANY` value to accept any token.

- PORTAL_BRIDGE_CONTRACTS

 > A comma-separated list of Portal Bridge contracts.

- PORTAL_BRIDGE_TOKENS_WHITELIST

  > An allowlist of tokens for the transfer which will trigger an airdrop of NEONs. This set should contain "tokenChain:tokenAddress", where:
  > - `tokenChain` is an original token chain number in terms of Portal bridge numbers
  > - `tokenAddress` is the address of the token in hexadecimal lowercase form with a '0x' prefix

- ERC20_BRIDGE_CONTRACTS

> A comma-separated list of Common ERC20 Bridge contracts

- ERC20_BRIDGE_TOKENS_WHITELIST

> An allowlist of tokens whose transfer triggers the airdrop of NEONs. This set should contains ERC20 addresses separated by a comma. Alt: provide the `ANY` value to accept any token.

## Gotchas

- PORTAL_BRIDGE_CONTRACTS & PORTAL_BRIDGE_TOKENS_WHITELIST should both be specified. If either is missed, the airdropper doesn't analyze Portal Bridge transfers.

- ERC20_BRIDGE_CONTRACTS & ERC20_BRIDGE_TOKENS_WHITELIST should both be specified. If they are missed, the airdropper doesn't analyze Common ERC20 Transfers.
