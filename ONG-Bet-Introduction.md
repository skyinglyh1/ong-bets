## ONG-Bet 游戏简介
#### 1. 与玩家有关的函数：
###### 1.1 bet()
```bet(account, ongAmount, number)``` -- 玩家参数游戏时需要调用的函数，该函数的功能是：

将玩家的ongAmount数量的ONG转入本合约(无需充值)，且合约产生随机数R。

若R小于number，则用户获胜，可获得```98 * ongAmount / (number - 1)```数量的ONG，函数执行成功后，用户已获得对应的ONG，无需提现。

否则用户输掉他的钱，用户的ongAmount数量的ONG保留在合约内部(作为合约管理员的收益)。

```angular2html
account -- 玩家的帐户地址

ongAmount -- 玩家想参与本游戏的ONG数量

number -- 玩家竞猜的数字，取值范围是2到96。(当产生的随机数小于该数字时，用户赢，否则，用户输) 

```

#### 2. 与庄家有关的操作（只有庄家可调用，若想成为庄家，需投资）：
###### 2.1 bankerInvest()

```bankerInvest(account, ongAmount)``` -- 任何人可通过投资该游戏成为庄家。
ongAmount的2%将给项目方作为服务费，48%将按份额分给以前的庄家作为之前庄家的分红收益，投资金额的50%将进入总资金池用于游戏运营。

###### 2.2 bankerWithdrawDividend()

```bankerWithdrawDividend(account)``` -- 庄家将自己的分红收益从合约内向自己的帐户进行提现。

###### 2.3 bankerWithdrawEarning()

```bankerWithdrawEarning(account)``` -- 庄家将自己分额的游戏收益从合约内向自己的帐户进行提现。
若本轮因总资金池的额度小于流入总资金池额度的10%，则本轮游戏结束，所有庄家对应的余额将会累计到自己分额的游戏收益中。

###### 2.4 bankerWithdraw()

```bankerWithdraw(account)``` -- 庄家将分红收益和自己分额的游戏收益从合约内向自己的帐户进行统一提现。

###### 2.5 bankerExit()

```bankerExit(account)``` -- 庄家若想退出，可立即按庄家共投入的资金池占所有庄家投入的资金池比例从当前资金池的总量中提现退出。同时，
 庄家将分红收益和自己分额的游戏收益从合约内向自己的帐户进行统一提现。


#### 3. 与合约管理员有关的函数（只有管理员可调用）：
###### 3.1 init()
```init(account, ongAmount, number)``` -- 合约布署成功后，需要管理员进行一次```init()```操作进行合约初始化。

###### 3.2 setParameters()

```setParameters(dividendForBankersPercentage, runningVaultPercentage)``` -- 
合约管理员设定庄家投资时的资金流向百分比，当前轮setParameters，则下轮生效，注意俩数之和应该为98。

###### 3.3 startNewRound()

```startNewRound(ongAmount)``` -- 合约管理员初始化新一轮游戏，同时传入合约管理员在本轮投资金额(以庄家的身份)。

###### 3.4 withdrawCommission()

```withdrawCommission(ongAmount)``` -- 合约管理员对服务费进行提现。


###### 3.3 migrateContract()

```migrateContract(code, needStorage, name, version, author, email, description, newReversedContractHash)``` -- 合约管理员迁移合约，功能为旧合约所有数据迁移到新合约内，且旧合约的所有ONG转入至新合约内。



#### 4. 对所有人公开的信息查询 (任何人都可通过预执行查询)
###### *** 公共全局信息 ***
###### 4.1 getCurrentRound()
```getCurrentRound()``` -- 查看当前游戏的轮数信息。
###### 4.2 getDividendForBankersPercentage(roundNumber)
```getDividendForBankersPercentage()``` -- 查看当前合约，第roundNumber轮时，当banker投资时，分红给之前所有庄家的分红百分比。
###### 4.3 getRunningVaultPercentage()
```getRunningVaultPercentage(roundNumber)``` -- 查看当前，第roundNumber轮时,当banker投资时，流入总资金池进行游戏运营的百分比。
###### 4.4 getTotalONG()
```getTotalONG()``` -- 查询当前合约帐户下的ONG余额。
###### 4.5 getCommission()
```getCommission()``` -- 查看合约管理员所有的服务费ONG余额。

###### *** 第roundNumber轮信息 ***
###### 4.6 getRoundGameStatus()
```getRoundGameStatus(roundNumber)``` -- 查看当前轮游戏的状态，{"RUNNING", "END"}。
###### 4.7 getBankersInvestment()
```getBankersInvestment(roundNumber)``` -- 查看第roundNumber轮的游戏内所有庄家的总投资额。
###### 4.8 getRunningVault()
```getRunningVault(roundNumber)``` -- 查看第roundNumber轮的游戏内总资金池内用于游戏运营的总投入。
###### 4.9 getRealTimeRunningVault()
```getRealTimeRunningVault(roundNumber)``` -- 查看第roundNumber轮的游戏内总资金池内用于游戏运营的总投入的实时余额。
###### 4.10 getBankersList()
```getBankersList(roundNumber)``` -- 查看第roundNumber轮的游戏内的所有庄家，返回一下list，每个元素为帐户地址。



###### *** account(banker) 信息 ***
###### 4.11 getBankerInvestment()
```getBankerInvestment(roundNumber, account)``` -- 查看第roundNumber轮的游戏内，account庄家的总投资额。
###### 4.12 getBankerBalanceInRunVault()
```getBankerBalanceInRunVault(roundNumber, account)``` -- 查看第roundNumber轮的游戏内，account庄家在总资金池(用于游戏运营)内的余额。
###### 4.13 getBankerDividend()
```getBankerDividend(account)``` -- 查看account庄家的分红收益。
###### 4.14 getBankerEarning()
```getBankerEarning(account)``` -- 查看account庄家的游戏运营收益。

