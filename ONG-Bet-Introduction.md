#ONG-Bet 游戏简介
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

#### 2. 与合约管理员有关的函数（只有管理员可调用）：
###### 2.1 init()
```init(account, ongAmount, number)``` -- 合约布署成功后，需要管理员进行一次```init()```操作进行合约初始化。

###### 2.2 invest()

```invest(ongAmount)``` -- 合约管理员向合约内投入ONG，用来支付用户获胜时赢取的ONG。

###### 2.3 withdraw()

```withdraw(ongAmount)``` -- 合约管理员从合约内向admin帐户提现。

###### 2.3 migrateContract()

```migrateContract(code, needStorage, name, version, author, email, description, newReversedContractHash)``` -- 合约管理员迁移合约，功能为旧合约所有数据迁移到新合约内，且旧合约的所有ONG转入至新合约内。



#### 3. 对所有人公开的信息查询
###### 3.1 getTotalONG()
```getTotalONG()``` -- 任何人都可通过预执行查询当前合约帐户下的ONG余额。
