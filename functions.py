from config import NETWORKS
from termcolor import cprint, colored
from web3 import Web3, HTTPProvider



def get_network():
    # Выбираем сеть
    keys = list(NETWORKS.keys())
    for key in enumerate(keys, 1):
        cprint(f'{key[0]}: {key[1]}', 'light_green')
    while True:
        try:
            choice = int(input("Выберите сеть в которой будет сделан свап: "))
            if choice < 1 or choice > len(keys):
                cprint("Некорректное число, повторите ввод!", 'light_yellow')
            else:
                selected_network = keys[choice - 1]
                cprint(f"Вы выбрали сеть {selected_network}")
                return selected_network, NETWORKS[selected_network]
        except ValueError:
            cprint("Некорректный символ, введите число!", 'light_yellow')


def get_out_token(rpc_url: str) -> str:
    # Получаем адрес токена на который будем переводить
    w3 = Web3(HTTPProvider(rpc_url))
    while True:
        token_address = input("Введите адрес токена на который будем переводить: ")
        # Проверка существования токена
        try:
            # Получение ABI токена (если известен)
            token_abi = w3.eth.get_code(token_address)
            if token_abi:
                cprint(f"Токен с адресом {token_address} существует.", 'light_green')
                return token_address
            else:
                cprint(f"Токен с адресом {token_address} не существует", 'light_yellow')
                continue
        except Exception as e:
            cprint(f"Ошибка при проверке токена: {e}", 'light_red')


def get_amount(balance: int) -> float:
    # Получаем количество токена для вывода в wei
    bal_human = balance / (10 ** 18)
    cprint(f"На вашем счету: {bal_human} нативного токена", 'light_green')
    while True:
        try:
            amount = float(input(colored("Введите сумму перевода нативного токена: ", 'light_green')))
            if amount <= 0:
                cprint(f" Пожалуйста, введите корректное число.", 'light_red')
                continue
            elif bal_human == 0:
                cprint(f" На вашем счету нет токенов", 'light_red')
                exit(1)
            elif bal_human < amount:
                cprint(f"Введенная сумма превышает баланс, попробуйте еще", 'light_red')
                continue
            return amount
        except ValueError:
            cprint("Пожалуйста, введите корректное число.", 'light_red')

def get_slippage()->float:
    while True:
        try:
            slippage = float(input(colored("Введите допустимый процент проскальзывания (Slippage) в %: ",
                                           'light_green')))
            if 0 < slippage < 100:
                return slippage
            else:
                cprint("Пожалуйста, введите корректное число.", 'light_yellow')
        except ValueError:
            cprint("Пожалуйста, введите корректное число.", 'light_red')

if __name__ == '__main__':
    #get_network()
    #check_outtoken('https://arbitrum.llamarpc.com')
    #get_amount(10000000000000000)
    get_slippage()