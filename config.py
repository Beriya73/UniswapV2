WETH_ADDRESS = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"

# Конфигурация сетей и контрактов
NETWORKS = {
    "Arbitrum one": {
        "rpc": f"https://arbitrum.llamarpc.com",
        "router": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
        "explorer": "https://arbiscan.io/",
    },
    "Optimism": {
        "rpc": f"https://optimism-mainnet.infura.io/v3/",
        "router": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
        "explorer": "https://optimistic.etherscan.io/",
    },
    "BNB_chain": {
        "rpc": f"https://bsc-dataseed.binance.org/",
        "router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
        "explorer": "https://bscscan.com/",
    },
    "Polygon": {
        "rpc": f"https://polygon-mainnet.infura.io/v3/",
        "router": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
        "explorer": "https://polygonscan.com/",
    }
}

