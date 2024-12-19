import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider
import os
from dotenv import load_dotenv
from termcolor import cprint
import json
from functions import (get_network,
                       get_out_token,
                       get_amount,
                       get_slippage)
from config import WETH_ADDRESS
from client import Client


# Загрузка переменных окружения из файла .env
load_dotenv()
private_key = os.getenv("PRIVATE_KEY")
proxy = os.getenv('proxy')


with open('uniswap2_abi.json') as file:
    UNISWAP_V2_ROUTER_ABI = json.load(file)

class UniswapV2Swap(Client):
    def __init__(self, private_key, proxy):
        super().__init__(private_key, proxy)
        self.chain_name, self.chain = get_network()
        self.input_token = WETH_ADDRESS  # ETH
        self.output_token = get_out_token(self.chain['rpc'])
        #self.amount = get_amount(self.balance())
        #self.slippage = slippage
        self.w3 = AsyncWeb3(AsyncHTTPProvider(self.chain['rpc']))
        self.private_key = private_key
        try:
            self.address = self.w3.to_checksum_address(
                self.w3.eth.account.from_key(self.private_key).address)  # Получение адреса кошелька
        except ValueError:
            cprint('Указанный private_key некорректен', 'light_red')
            exit(1)
        self.router_contract = self.w3.eth.contract(address=self.chain['router'], abi=UNISWAP_V2_ROUTER_ABI)
        self.explorer_url = self.chain['explorer']

    async def balance(self):
        balance = await self.w3.eth.get_balance(self.address)
        return balance

    async def get_amounts_out(self,amount):
        self.path = [WETH_ADDRESS, self.output_token]
        amounts = await self.router_contract.functions.getAmountsOut(amount, self.path).call()

        return amounts[-1]

    async def exact_eth_for_tokens(self, slippage, amount):
        amount_out_min = int(await self.get_amounts_out(amount) * (1 - slippage / 100))
        last_block = await self.w3.eth.get_block('latest')
        deadline = last_block.get('timestamp') + 300

        transaction = await self.router_contract.functions.swapExactETHForTokens(
            amount_out_min,
            self.path,
            self.address,
            deadline
        ).build_transaction(await self.prepare_tx(amount))
        await self.send_transaction(transaction=transaction)

async def main():
    swap = UniswapV2Swap(private_key, proxy)
    amount = int(get_amount(await swap.balance())*10**18)
    slippage = get_slippage()
    await swap.exact_eth_for_tokens(slippage, amount)


asyncio.run(main())
