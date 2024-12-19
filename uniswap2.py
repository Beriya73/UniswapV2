import asyncio
from web3 import AsyncWeb3, AsyncHTTPProvider
import os
from dotenv import load_dotenv
from termcolor import cprint
import json
from functions import (get_network,
                       get_token_addr,
                       get_amount,
                       get_slippage)
from client import Client

# Загрузка переменных окружения из файла .env
load_dotenv()
private_key = os.getenv("PRIVATE_KEY")
proxy = os.getenv('proxy')

with open('uniswap2_abi.json') as file:
    UNISWAP_V2_ROUTER_ABI = json.load(file)

class UniswapV2Swap(Client):
    """
    Класс для выполнения свапов на платформе Uniswap V2 в сети Arbitrum.
    """
    def __init__(self, private_key, proxy):
        """
        Инициализация класса UniswapV2Swap.

        Параметры:
            private_key (str): Приватный ключ кошелька.
            proxy (str): Прокси для подключения к сети.
        """
        super().__init__(private_key, proxy)
        self.chain_name, self.chain = get_network()
        self.input_token = get_token_addr(self.chain['rpc'], 'Введите адрес токена с которого будем переводить: ')
        self.output_token = get_token_addr(self.chain['rpc'], 'Введите адрес токена на который будем переводить: ')
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
        """
        Получает баланс кошелька.

        Возвращает:
            int: Баланс кошелька в wei.
        """
        balance = await self.w3.eth.get_balance(self.address)
        return balance

    async def get_amounts_out(self, amount):
        """
        Получает количество токенов, которые будут получены в результате свапа.

        Параметры:
            amount (int): Количество ETH для свапа.

        Возвращает:
            int: Количество токенов, которые будут получены.
        """
        self.path = [self.input_token, self.output_token]
        amounts = await self.router_contract.functions.getAmountsOut(amount, self.path).call()
        return amounts[-1]

    async def exact_eth_for_tokens(self, slippage, amount):
        """
        Выполняет свап ETH на токены с учетом проскальзывания.

        Параметры:
            slippage (float): Допустимый процент проскальзывания.
            amount (int): Количество ETH для свапа.
        """
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
    """
    Основная функция для выполнения свапа.
    """
    swap = UniswapV2Swap(private_key, proxy)
    amount = int(get_amount(await swap.balance()) * 10**18)
    slippage = get_slippage()
    await swap.exact_eth_for_tokens(slippage, amount)

asyncio.run(main())
