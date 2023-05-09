from scripts import deploy_liquid_path, deploy_swap_router
from scripts.utils.polybit_utils import get_account
from brownie import (
    config,
)
from web3 import Web3
import json
import urllib.request, json
import time

WETH = config["networks"]["bsc-main"]["weth_address"]


def main():
    polybit_owner_account = get_account(type="polybit_owner")
    print("Polybit Owner", polybit_owner_account.address)

    polybit_swap_router = deploy_swap_router.main(
        polybit_owner_account,
    )

    polybit_liquid_path = deploy_liquid_path.main(
        polybit_owner_account, polybit_swap_router.address
    )

    print("Swap Router Address", polybit_swap_router.address)
    # print("Swap Router ABI",polybit_swap_router.abi)

    print("Liquid Path Address", polybit_liquid_path.address)
    # print("Liquid Path ABI",polybit_liquid_path.abi)

    """
    Test swap
    """
    amount_in = 1 * 10**18
    amount_type = 0
    slippage = 0.01

    TEST_ASSETS = [
        "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
        "0xBf5140A22578168FD562DCcF235E5D43A02ce9B1",
        "0x8F0528cE5eF7B51152A59745bEfDD91D97091d2F",
        "0xac51066d7bec65dc4589368da368b212745d63e8",
        "0x949D48EcA67b17269629c7194F4b727d4Ef9E5d6",
    ]

    for i in range(0, len(TEST_ASSETS)):
        factory_address, path, amount_out = polybit_liquid_path.getLiquidPath(
            WETH, TEST_ASSETS[i], amount_in, amount_type
        )
        print("AmountsOut", factory_address, path, amount_out)

        amount_out_min = amount_out * (1 - slippage)
        tx = polybit_swap_router.swapExactETHForTokens(
            factory_address,
            path,
            amount_out_min,
            polybit_owner_account.address,
            int(time.time() + 300),
            {"from": polybit_owner_account, "value": amount_in},
        )
        tx.wait(1)
