from binance.um_futures import UMFutures
import creds
import pandas as pd
import logging
import math
from binance.error import ClientError
import time

binance_api_key = creds.binance_api_key
binance_api_secret = creds.binance_api_secret
binance_client = UMFutures(binance_api_key,binance_api_secret,base_url="https://testnet.binancefuture.com")

account = binance_client.account()
df_assets = pd.DataFrame(account["assets"])

#Get available USDT balance
def getUsdtBalance():        
    usdt_row = df_assets.loc[df_assets["asset"] == "USDT"]
    balance = float(usdt_row["availableBalance"])
    balance = round(balance,3)
    return float(balance)

#Creates a position for the given symbol
def createPosition(symbol, position_cost, leverage, position_type, entry_target):
    decimal = getRoundCount(symbol=symbol)
    try:
        response2 = binance_client.change_leverage(
            symbol = symbol, leverage = leverage
        )
        response1 = binance_client.new_order(
            symbol = symbol,
            side = position_type,
            type = "LIMIT",
            quantity = float(round((position_cost/entry_target),decimal)),
            #float(round((position_cost/entry_target),8)),
            leverage = leverage,
            timeInForce = "GTC",
            price = entry_target
        )
    except ClientError as error:
        print("Create Position - Found error. Status {}, Error Code: {}, Error Message: {}".format(error.status_code, error.error_code, error.error_message))
    else:
        print("Position created succesfully!")

        
#Sets Take Profit Level for the given symbol
def setTakeProfit(symbol, quantity, leverage, position_type, take_profit):
    try:
        response2 = binance_client.change_leverage(
            symbol = symbol, leverage = leverage
        )
        response1 = binance_client.new_order(
            symbol = symbol,
            side = position_type,
            type = "TAKE_PROFIT",
            leverage = leverage,
            timeInForce = "GTC",
            price = take_profit, 
            stopPrice = take_profit, 
            quantity = quantity 
        )
    except ClientError as error:
        print("Take Profit Position - Found error. Status {}, Error Code: {}, Error Message: {}".format(error.status_code, error.error_code, error.error_message))
    else:
        print("Take Profit position created succesfully!")


#Sets a Stop Loss for the given symbol
def setStopLoss(symbol, quantity, leverage, position_type, entry_target):
    price = 0
    if position_type == "SELL":
        price = entry_target*(1.14)
    elif position_type == "BUY":
        price = entry_target*(0.86)
    try:
        response2 = binance_client.change_leverage(
            symbol = symbol, leverage = leverage
        )
        response1 = binance_client.new_order(
            symbol = symbol,
            side = position_type,
            type = "STOP",
            leverage = leverage,
            timeInForce = "GTC",
            price = price, 
            stopPrice = price, 
            quantity = quantity 
        )
    except ClientError as error:
        print("Stop Loss Position - Found error. Status {}, Error Code: {}, Error Message: {}".format(error.status_code, error.error_code, error.error_message))
    else:
        print("Stop Loss position created succesfully!")


#Gets the latest order's position quantity

#def getOrderQuantity(symbol):
#    try:
        """
        response = binance_client.get_orders(symbol = symbol)
        df_response = pd.DataFrame(response)
        latest_order = df_response.iloc[-1]
        if latest_order == None:
            response = binance_client.get_open_orders(symbol=symbol)
            df_response = pd.DataFrame(response)
            latest_order = df_response.iloc[-1]
        """
        """
        latest_order_quantity = 0.0
        orders = binance_client.get_all_orders(symbol)
        orders = sorted(orders, key=lambda order: order["orderId"], reverse=True)
        latest_order = orders[0]
        if latest_order["status"] in ["FILLED","PARTIALLY_FILLED"]:
            open_orders = binance_client.get_open_orders(symbol,binance_client.time())
            latest_open_order = next(filter(lambda order: order["orderId"] == latest_order["orderId"], open_orders))
            latest_order_quantity = latest_open_order["quantity"]
        else:
            latest_order_quantity = latest_order["quantity"]

        #order_quantity = float(latest_order["origQty"])
    except ClientError as error:
        print("Get Order Quantity - Found error. Status {}, Error Code: {}, Error Message: {}".format(error.status_code, error.error_code, error.error_message))
    return round(latest_order_quantity,3)
"""

#Gets the allowed LOT_SIZE for the given symbol
def getRoundCount(symbol):
    exchance_info = binance_client.exchange_info()
    symbols = exchance_info["symbols"] 
    for i in symbols:
        if i["symbol"] == symbol:
            filters = i["filters"]
            df_filters = pd.DataFrame(filters)
            df_filters.set_index("filterType", inplace=True)
            lot_size_row = df_filters.loc["LOT_SIZE"]
            minQty = lot_size_row["minQty"]
            count_after_decimal = str(minQty)[::-1].find('.')
            return count_after_decimal
            

def setTPandSL(symbol, leverage, position_type, entry_target, take_profit ):
    try:
        latest_order_quantity = 0.0
        orders = binance_client.get_all_orders(symbol)
        orders = sorted(orders, key=lambda order: order["orderId"], reverse=True)
        df_orders = pd.DataFrame(orders)
        latest_order = df_orders.iloc[0]

        if latest_order["status"] in ["FILLED", "PARTIALLY_FILLED"]:
            quantity = latest_order["origQty"]
            setStopLoss(symbol,quantity, leverage, position_type, entry_target)
            setTakeProfit(symbol,quantity,leverage,position_type,take_profit)
            print("Successfully placed Stop Loss and Take Profit orders")
       
        elif latest_order["status"] == "NEW":
            for sec in range(300):
                if(latest_order["status"] in ["FILLED","PARTIALLY_FILLED"]):
                    quantity = latest_order["origQty"]
                    setStopLoss(symbol,quantity, leverage, position_type, entry_target)
                    setTakeProfit(symbol,quantity,leverage,position_type,take_profit)
                    print("Successfully placed Stop Loss and Take Profit orders")
                    break
                elif latest_order["status"] == "NEW":
                    time.sleep(1)
                else:
                    break
            
    except ClientError as error:
        print("Get Order Quantity - Found error. Status {}, Error Code: {}, Error Message: {}".format(error.status_code, error.error_code, error.error_message))