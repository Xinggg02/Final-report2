# 載入必要函數
import indicator,sys,time,datetime,haohaninfo,order_Lo3_test4
from haohaninfo import MicroPlay
import lineTool
from haohaninfo.MicroTest import microtest_db
import numpy as np



Broker = 'Test'
Prod = 'MXFH9'   
KMinute= 1
ShortMAPeriod=2
LongMAPeriod=3
O_B_Qty = '3'
O_S_Qty = '3'
StopLoss = 30
StopLossPoint_B = 0
StopLossPoint_S = 100000000000
wait_O = 20 
wait_C = 6000 
 

token='JbsJ53TwusWdldM8a5i6dg5tBTVbz7jSUlRgjIStEFy'




RC=order_Lo3_test4.Record()

Today = '20190731'        
KBar = indicator.KBar(Today,KMinute) 

a = MicroPlay.MicroPlayQuote()
for row in a.Subscribe(Broker, 'match', Prod):
    CTime = datetime.datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S.%f')
    CPrice=float(row[2])
    CQty=int(row[3])
    if KBar.AddPrice(CTime,CPrice,CQty) == 1:
        CloseList=KBar.GetClose()
        if len(CloseList) >= LongMAPeriod+2:
            LongMAList = KBar.GetEMA(LongMAPeriod)
            ShortMAList=KBar.GetEMA(ShortMAPeriod)
            ClosePrice=CloseList[-2]
            LongMA=LongMAList[-2]
            ShortMA=ShortMAList[-2]
            LastClosePrice=CloseList[-3]
            LastLongMA=LongMAList[-3]
            LastShortMA=ShortMAList[-3]
            print('目前在倉部位口數:',RC.GetOpenInterest(),'目前成交報價資料時間:',CTime,'最新收盤價:',ClosePrice,'上一筆收盤價:',LastClosePrice,'最新短MA:',ShortMA,'上一筆短MA:',LastShortMA,'最新長MA:',LongMA,'上一筆長MA:',LastLongMA)
            print()
            if RC.GetOpenInterest() == 0:
                if LastShortMA <= LastLongMA and ShortMA > LongMA:
                    OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'B',O_B_Qty,'0',2,wait_O)  
                    if OrderInfo == False: 
                        a.EndSubscribe()
                    else:
                        for i in OrderInfo:
                           OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                           OrderInfoPrice=float(i.split(',')[4])
                           OrderProd = i.split(',')[2]
                           OrderQty = i.split(',')[5]
                           RC.Order('B',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                           StopLossPoint_B= max(OrderInfoPrice-StopLoss,StopLossPoint_B) 
                           print('交易編號:',i.split(',')[0] ,', 產品:', OrderProd,', 多單進場買進時間:',OrderInfoTime,', 買進價格:',OrderInfoPrice,', 停損價位:',StopLossPoint_B,', 多單成交買進口數:',OrderQty,', 多單委託買進口數:',O_B_Qty)
                           print()
                           msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 多單買進時間: '+str(OrderInfoTime)+'; 買進價格: '+str(OrderInfoPrice)+'; 多單成交買進口數: '+str(OrderQty)+'; 多單委託買進口數: '+str(O_B_Qty)
                           lineTool.lineNotify(token,msg)
                elif LastShortMA >= LastLongMA and ShortMA < LongMA:
                    OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'S',O_S_Qty,'0',2,wait_O)
                    if OrderInfo == False:
                        a.EndSubscribe()
                    else:
                        for i in OrderInfo:
                           OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                           OrderInfoPrice=float(i.split(',')[4])
                           OrderProd = i.split(',')[2]
                           OrderQty = i.split(',')[5]
                           RC.Order('S',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                           StopLossPoint_S= min(OrderInfoPrice+StopLoss,StopLossPoint_S)  ## 還有小問題
                           print('交易編號:',i.split(',')[0] ,', 產品:',OrderProd,', 空單買進時間:',OrderInfoTime,', 買進價格:',OrderInfoPrice,', 停損價位:',StopLossPoint_S,', 空單成交買進口數:',OrderQty,', 空單委託買進口數:',O_S_Qty)
                           print()
                           msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 空單買進時間: '+str(OrderInfoTime)+'; 買進價格: '+str(OrderInfoPrice)+'; 空單成交買進口數: '+str(OrderQty)+'; 空單委託買進口數: '+str(O_S_Qty)
                           lineTool.lineNotify(token,msg)
            elif RC.GetOpenInterest() > 0:    
                if ClosePrice-StopLoss > StopLossPoint_B:
                    StopLossPoint_B=ClosePrice-StopLoss 
                elif ClosePrice <= StopLossPoint_B:
                    C_S_Qty = RC.GetOpenInterest()   
                    OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'S',C_S_Qty,'0',2,wait_C)
                    
                    if OrderInfo == False:
                        a.EndSubscribe()
                    else:
                        for i in OrderInfo:
                           OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                           OrderInfoPrice=float(i.split(',')[4])
                           OrderProd = i.split(',')[2]
                           OrderQty = i.split(',')[5]
                           MicroTest_Qty = OrderQty
                           RC.Cover('S',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                           print('交易編號:',i.split(',')[0] ,', 產品:',OrderProd,', 多單平倉時間:',OrderInfoTime,', 平倉價格:',OrderInfoPrice,', 多單成交平倉口數:',OrderQty,', 多單委託平倉口數:',C_S_Qty)
                           print()
                           msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 多單平倉時間: '+str(OrderInfoTime)+'; 平倉價格: '+str(OrderInfoPrice)+'; 多單成交平倉口數: '+str(OrderQty)+'; 多單委託平倉口數: '+str(C_S_Qty)
                           lineTool.lineNotify(token,msg)
                        a.EndSubscribe()
            elif RC.GetOpenInterest() < 0:     
                if ClosePrice+StopLoss < StopLossPoint_S:
                    StopLossPoint_S=ClosePrice+StopLoss 
                elif ClosePrice >= StopLossPoint_S:
                    C_B_Qty = -(RC.GetOpenInterest())   
                    OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'B',C_B_Qty,'0',2,wait_C)
                    
                    if OrderInfo == False:
                        a.EndSubscribe()
                    else:
                        for i in OrderInfo:
                           OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                           OrderInfoPrice=float(i.split(',')[4])
                           OrderProd = i.split(',')[2]
                           OrderQty = i.split(',')[5]
                           MicroTest_Qty = OrderQty
                           RC.Cover('B',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                           print('交易編號:',i.split(',')[0] ,', 產品:',OrderProd,', 空單平倉時間:',OrderInfoTime,', 平倉價格:',OrderInfoPrice,', 空單成交平倉口數:',OrderQty,', 空單委託平倉口數:',C_B_Qty)
                           print()
                           msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 空單平倉時間: '+str(OrderInfoTime)+'; 平倉價格: '+str(OrderInfoPrice)+'; 空單成交平倉口數: '+str(OrderQty)+'; 空單委託平倉口數: '+str(C_B_Qty)
                           lineTool.lineNotify(token,msg)
                        a.EndSubscribe()
                

#print('交易紀錄:',RC.TradeRecord)
print('交易紀錄:',RC.GetTradeRecord())
print('在倉部位數量:',RC.GetOpenInterest())  
print('在倉部位清單:',RC.OpenInterest)
print('績效記錄清單:',RC.GetProfit())
print('淨交易績效:', RC.GetTotalProfit(), ', 平均每次交易績效(包含盈虧):',RC.GetAverageProfit(), ', 勝率(賺錢次數占總次數比例):',RC.GetWinRate(),', 最大連續虧損:', RC.GetAccLoss(), ', 最大資金(績效profit)回落(MDD):',RC.GetMDD(),', 平均每次獲利(只算賺錢的):',RC.GetAverEarn(),', 平均每次虧損(只算賠錢的):',RC.GetAverLoss())

## 產出累積績效圖(包含盈虧):
RC.GeneratorProfitChart()

## MicroTest:
RC.FutureMicroTestRecord(StrategyName='MA',ProductValue=50,Fee=100,volume=MicroTest_Qty,account='pu25',password='pu25')  

def FutureMicroTestRecord(StrategyName,ProductValue,Fee,volume,account,password):
        microtest_db.login(account,password,'140.128.36.207')
        for row in RC.TradeRecord:
            Tax=(row[3]+row[5])*ProductValue*0.00002
            microtest_db.insert_to_server_db(row[1],row[2].strftime('%Y-%m-%d'),row[2].strftime('%H:%M:%S'),str(int(row[3])),str(row[0]),str(volume),row[4].strftime('%Y-%m-%d'),row[4].strftime('%H:%M:%S'),str(row[5]),str(int(Tax)),str(int(Fee)),StrategyName) 
        microtest_db.commit()

FutureMicroTestRecord(StrategyName='MA',ProductValue=50,Fee=100,volume=MicroTest_Qty,account='pu25',password='pu25')


