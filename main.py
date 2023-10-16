import creds
import asyncio
from telethon import TelegramClient, events
import binanceAPI


tele_api_id = creds.tele_api_id
tele_api_hash = creds.tele_api_hash
telegram_client = TelegramClient('anon', tele_api_id, tele_api_hash)

#!==========================================================================================
#?                                       TELEGRAM PART
#!==========================================================================================


chat = creds.telegram_test
@telegram_client.on(events.NewMessage(chats = chat))
async def main(event):
    #Get channels name and id
    """
    async for i in client.iter_dialogs():
        channelId = i.entity.id
        channelName = i.name
        print("Channel name: {}, Channel id: {}".format(channelName,channelId))
    """

    text = event.text
    text = text.upper()
    textList = text.split()

    if(textList[0] == "LONG" or textList[0] == "SHORT"):
        position_type = ""
        opposite_position_type = ""
        if textList[0] == "LONG":
            position_type = "BUY"
            opposite_position_type = "SELL"
        else:
            position_type = "SELL"
            opposite_position_type = "BUY"

        balance = binanceAPI.getUsdtBalance()
        cost_per_position = 100.0

        #?Create Position with Stop Loss and Take Profit if balance is greater than cost_per_position amount.
        if balance >= cost_per_position:
            print("Balance is greater than", cost_per_position)
            position_cost = cost_per_position
            symbol = textList[1].replace("/","")
            leverage= 5
            entry1 = textList[6]
            entry1 = float(entry1[2::])
            tp1 = textList[10]
            tp1 = float(tp1[2::])
            
            try:
            #Create a position according to the signal
                binanceAPI.createPosition(symbol,position_cost,leverage,position_type,entry1)
            #Get the latest order quantity of the symbol in order to close the position at Take-Profit level
            except binanceAPI.ClientError as error:
                print("Error has occured")
            else:
                orderQty = binanceAPI.getOrderQuantity(symbol)
                #Create a closing position acccording to the signal
                #binanceAPI.closePosition(symbol,orderQty,leverage,opposite_position_type,tp1)

                #Sets stop loss and take profits
                binanceAPI.setTPandSL(symbol,leverage,opposite_position_type,entry1,tp1)
                print("*************************************")
                print(f"Position: {position_type}\nSymbol: {symbol}\nLeverage: {leverage}\nEntry Level: {entry1}\nTake-Profit Level: {tp1}")
                print("-------------------------------------")
    else:
        print("Not a signal")
        print("-------------------------------------")

telegram_client.start()
telegram_client.run_until_disconnected()



