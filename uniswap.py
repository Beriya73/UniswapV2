import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider
from web3.exceptions import TransactionNotFound
import os
from dotenv import load_dotenv
from termcolor import cprint
import json

# Загрузка переменных окружения из файла .env
load_dotenv()
private_key = os.getenv("PRIVATE_KEY")

# Конфигурация сетей и контрактов
NETWORKS = {
    "arbitrum": {
        "rpc": f"https://arbitrum.llamarpc.com",
        "router": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
        "explorer": "https://arbiscan.io/",
    },
    "optimism": {
        "rpc": f"https://optimism-mainnet.infura.io/v3/{infura_project_id}",
        "router": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
        "explorer": "https://optimistic.etherscan.io/",
    },
    "bnb_chain": {
        "rpc": f"https://bsc-dataseed.binance.org/",
        "router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
        "explorer": "https://bscscan.com/",
    },
    "polygon": {
        "rpc": f"https://polygon-mainnet.infura.io/v3/{infura_project_id}",
        "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
        "explorer": "https://polygonscan.com/",
    }
}

# Адреса токенов
WETH_ADDRESS = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
ta = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
with open('uniswap2_abi.json') as file:
    UNISWAP_V2_ROUTER_ABI = json.load(file)

class UniswapV2Swap:
    def __init__(self, network, input_token, output_token, amount, slippage):
        self.network = network
        self.input_token = input_token
        self.output_token = output_token
        self.amount = amount
        self.slippage = slippage
        self.w3 = AsyncWeb3(AsyncHTTPProvider(NETWORKS[network]['rpc']))
        self.private_key = private_key
        try:
            self.address = self.w3.to_checksum_address(
                self.w3.eth.account.from_key(self.private_key).address)  # Получение адреса кошелька
        except ValueError:
            cprint('Указанный private_key некорректен', 'light_red')
            exit(1)
        self.router_contract = self.w3.eth.contract(address=NETWORKS[network]['router'], abi=UNISWAP_V2_ROUTER_ABI)
        self.explorer_url = NETWORKS[network]['explorer']

    async def check_balance(self):
        balance = await self.w3.eth.get_balance(self.address)
        if balance < self.amount:
            cprint(f"Недостаточно средств на кошельке. Баланс: {balance / (10 ** 18)} ETH", 'light_red')
            exit(1)
        return balance

    async def get_amounts_out(self):
        self.path = [WETH_ADDRESS, self.output_token]
        amounts = await self.router_contract.functions.getAmountsOut(self.amount, self.path).call()

        return amounts[-1]

    async def swap_exact_eth_for_tokens(self):
        amount_out_min = int(await self.get_amounts_out() * (1 - self.slippage / 100))
        last_block = await self.w3.eth.get_block('latest')
        deadline = last_block.get('timestamp') + 300


        tx = await self.router_contract.functions.swapExactETHForTokens(
            amount_out_min,
            self.path,
            self.address,
            deadline
        ).build_transaction({
            'from': self.address,
            'value': self.amount,
            'nonce': await self.w3.eth.get_transaction_count(self.address),
            'gas': 2000000,
            'gasPrice': await self.w3.eth.gas_price,
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        return tx_hash

    async def wait_for_transaction(self, tx_hash):
        total_time = 0
        timeout = 120
        poll_latency = 10
        while True:
            try:
                receipt = await self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt is not None:
                    if receipt['status'] == 1:
                        cprint(f'Transaction was successful: {self.explorer_url}tx/{tx_hash}', 'light_green')
                        return True
                    else:
                        cprint(f'Transaction failed: {self.explorer_url}tx/{tx_hash}', 'light_red')
                        return False
            except TransactionNotFound:
                if total_time > timeout:
                    cprint(f"Transaction is not in the chain after {timeout} seconds", 'light_yellow')
                    return False
                total_time += poll_latency
                await asyncio.sleep(poll_latency)

async def main():
    #network = input("Выберите сеть (arbitrum, optimism, bnb_chain, polygon): ").lower()
    network = 'arbitrum'
    input_token = WETH_ADDRESS  # ETH
    # output_token = input("Введите адрес выходящей монеты: ")
    output_token = "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9"
    amount = int(float(input("Введите количество ETH для свапа: ")) * 10**18)
    slippage = float(input("Введите допустимый процент проскальзывания (Slippage) в %: "))

    swap = UniswapV2Swap(network, input_token, output_token, amount, slippage)
    await swap.check_balance()
    tx_hash = await swap.swap_exact_eth_for_tokens()
    await swap.wait_for_transaction(tx_hash)

if __name__ == "__main__":
    asyncio.run(main())
