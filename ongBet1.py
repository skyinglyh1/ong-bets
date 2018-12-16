from boa.interop.Ontology.Contract import Migrate
from boa.interop.System.Storage import GetContext, Get, Put, Delete
from boa.interop.System.Runtime import CheckWitness, GetTime, Notify, Serialize, Deserialize
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash, GetEntryScriptHash, GetScriptContainer
from boa.interop.Ontology.Native import Invoke
from boa.interop.Ontology.Runtime import GetCurrentBlockHash
from boa.builtins import ToScriptHash, concat, state
from boa.interop.System.Transaction import GetTransactionHash

# the script hash of this contract
ContractAddress = GetExecutingScriptHash()
ONGAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02')
# E.T account
# Admin = ToScriptHash("ARiYs54Kq9T5h3QY1xTyXGb9gsJ1TUbMB7")
# skyinglyh account
Admin = ToScriptHash("AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p")

INITIALIZED = "Init"
TOTAL_ONG_KEY = "TotalONG"
COMMISSION_KEY = "Commission"

ROUND_PREFIX = "G01"
CURRENT_ROUND_KEY = "G02"
# ROUND_PREFIX + CURRENT_ROUND_KEY + ROUND_STATUS
ROUND_STATUS = "G03"
# ROUND_PREFIX + CURRENT_ROUND_KEY + DIVIDEND_FOR_BANKERS_PERCENTAGE  -- to store 48
DIVIDEND_FOR_BANKERS_PERCENTAGE = "G04"
# ROUND_PREFIX + CURRENT_ROUND_KEY + RUNNING_VAULT_PERCENTAGE -- to store 50
RUNNING_VAULT_PERCENTAGE = "G05"
# ROUND_PREFIX +  CURRENT_ROUND_KEY + BANKERS_LIST_KEY
BANKERS_LIST_KEY = "G06"
# ROUND_PREFIX + CURRENT_ROUND_KEY + BANKERS_INVESTMENT_KEY -- total investment
BANKERS_INVESTMENT_KEY = "G07"
# ROUND_PREFIX + CURRENT_ROUND_KEY + INCREASING_RUN_VAULT_KEY -- ong that has been added into the running vault
INCREASING_RUN_VAULT_KEY = "G08"
# ROUND_PREFIX + CURRENT_ROUND_KEY + REAL_TIME_RUNNING_VAULT -- running vault except the earnings, ong that can be paid to the players
REAL_TIME_RUNNING_VAULT = "G09"
# ROUND_PREFIX + CURRENT_ROUND_KEY + PROFIT_PER_INVESTMENT_FOR_BANKERS_KEY
PROFIT_PER_INVESTMENT_FOR_BANKERS_KEY = "G10"
PROFIT_PER_RUNNING_VAULT_SHARE_KEY = "G11"

# ROUND_PREFIX + CURRENT_ROUND_KEY + PROFIT_PER_INVESTMENT_FOR_BANKER_FROM_KEY + account
PROFIT_PER_INVESTMENT_FOR_BANKER_FROM_KEY = "U01"
PROFIT_PER_RUNNING_VAULT_SHARE_FROM_KEY = "U02"
# ROUND_PREFIX + CURRENT_ROUND_KEY + BANKER_INVEST_BALANCE_PREFIX + account -> ong that has been invested into this game by the banker(account)
BANKER_INVEST_BALANCE_PREFIX = "U03"
# BANKER_LAST_TIME_UPDATE_DIVIDEND_ROUND_KEY + account  -- store the round number the banker last time updates his dividend
BANKER_LAST_TIME_UPDATE_DIVIDEND_ROUND_KEY = "U04"
# BANKER_LAST_TIME_UPDATE_EARNING_ROUND_KEY + account  -- store the round number the banker last time updates his earning
BANKER_LAST_TIME_UPDATE_EARNING_ROUND_KEY = "U05"
# BANKER_DIVIDEND_BALANCE_PREFIX + account -- store the account's dividend as a banker
BANKER_DIVIDEND_BALANCE_PREFIX = "U06"
# BANKER_DIVIDEND_BALANCE_PREFIX + account -- store the account's shared earning as a banker from the running vault
BANKER_EARNING_BALANCE_PREFIX = "U07"
# # BANKER_WITHDRAWN_BALANCE_KEY + account -- store the account's withdrawn amount of ong
# BANKER_WITHDRAWN_BALANCE_KEY = "U09"
bankerQuota = 1000000000000

STATUS_ON = "RUNNING"
STATUS_OFF = "END"

MagnitudeForProfitPerSth = 1000000000000000000000000000000

def Main(operation, args):
    ############### for Admin to invoke Begin ##################
    if operation == "init":
        return init()
    if operation == "setParameters":
        if len(args) != 2:
            return False
        dividendForBankersPercentage = args[0]
        runningVaultPercentage = args[1]
        return setParameters(dividendForBankersPercentage, runningVaultPercentage)
    if operation == "withdrawCommission":
        return withdrawCommission()
    if operation == "migrateContract":
        if len(args) != 8:
            return False
        code = args[0]
        needStorage = args[1]
        name = args[2]
        version = args[3]
        author = args[4]
        email = args[5]
        description = args[6]
        newReversedContractHash = args[7]
        return migrateContract(code, needStorage, name, version, author, email, description, newReversedContractHash)
    ############### for Admin to invoke End ##################
    ############### for Bankers to invoke Begin ##################
    if operation == "bankerInvest":
        if len(args) != 2:
            return False
        account = args[0]
        ongAmount = args[1]
        return bankerInvest(account, ongAmount)
    if operation == "bankerWithdraw":
        if len(args) != 1:
            return False
        account = args[0]
        return bankerWithdraw(account)
    if operation == "bankerExit":
        if len(args) != 1:
            return False
        account = args[0]
        return bankerExit(account)
    ############### for Bankers to invoke End ##################
    ############### for players to invoke Begin ##################
    if operation == "bet":
        if len(args) != 3:
            return False
        account = args[0]
        ongAmount = args[1]
        number = args[2]
        return bet(account, ongAmount, number)
    ############### for players to invoke End ##################
    ############### for all to pre-invoke Begin ##################
    if operation == "getCurrentRound":
        return getCurrentRound()
    if operation == "getDividendForBankersPercentage":
        if len(args) != 1:
            return False
        roundNumber = args[0]
        return getDividendForBankersPercentage(roundNumber)
    if operation == "getRunningVaultPercentage":
        if len(args) != 1:
            return False
        roundNumber = args[0]
        return getRunningVaultPercentage(roundNumber)
    if operation == "getTotalONG":
        return getTotalONG()
    if operation == "getCommission":
        return getCommission()
    if operation == "getRoundGameStatus":
        if len(args) != 1:
            return False
        roundNumber = args[0]
        return getRoundGameStatus(roundNumber)
    if operation == "getBankersInvestment":
        if len(args) != 1:
            return False
        roundNumber = args[0]
        return getBankersInvestment(roundNumber)
    if operation == "getIncreasingRunnVault":
        if len(args) != 1:
            return False
        roundNumber = args[0]
        return getIncreasingRunnVault(roundNumber)
    if operation == "getRunningVault":
        if len(args) != 1:
            return False
        roundNumber = args[0]
        return getRunningVault(roundNumber)
    if operation == "getRealTimeRunningVault":
        if len(args) != 1:
            return False
        roundNumber = args[0]
        return getRealTimeRunningVault(roundNumber)
    if operation == "getBankersList":
        if len(args) != 2:
            return False
        roundNumber = args[0]
        includeExitBankers = args[1]
        return getBankersList(roundNumber, includeExitBankers)
    ############### for all to pre-invoke End ##################
    ############### for bankers to pre-invoke Begin ##################
    if operation == "getBankerInvestment":
        if len(args) != 2:
            return False
        roundNumber = args[0]
        account = args[1]
        return getBankerInvestment(roundNumber, account)
    if operation == "getBankerBalanceInRunVault":
        if len(args) != 2:
            return False
        roundNumber = args[0]
        account = args[1]
        return getBankerBalanceInRunVault(roundNumber, account)
    if operation == "getBankerDividend":
        if len(args) != 1:
            return False
        account = args[0]
        return getBankerDividend(account)
    if operation == "getBankerEarning":
        if len(args) != 1:
            return False
        account = args[0]
        return getBankerEarning(account)
    if operation == "getRunVaultShare":
        if len(args) != 1:
            return False
        account = args[0]
        return getRunVaultShare(account)
    ############### for bankers to pre-invoke End ##################
    # for test usage
    if operation == "getProfitPerInvestmentForBankers":
        if len(args) != 1:
            return False
        roundNumber = args[0]
        return getProfitPerInvestmentForBankers(roundNumber)
    if operation == "getProfitPerRunningVaultShare":
        if len(args) != 1:
            return False
        roundNumber = args[0]
        return getProfitPerRunningVaultShare(roundNumber)
    if operation == "getBankersLastTimeUpdateDividendRound":
        if len(args) != 1:
            return False
        account = args[0]
        return getBankersLastTimeUpdateDividendRound(account)
    if operation == "getBankersLastTimeUpdateEarnRound":
        if len(args) != 1:
            return False
        account = args[0]
        return getBankersLastTimeUpdateEarnRound(account)
    if operation == "_rollANumber":
        return _rollANumber()
    return False

############### for Admin to invoke Begin ##################
def init():
    RequireWitness(Admin)
    inited = Get(GetContext(), INITIALIZED)
    if inited:
        Notify(["Idiot admin, you have initialized the contract!"])
        return False
    else:
        Put(GetContext(), INITIALIZED, 'Y')
        Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, 0), ROUND_STATUS), STATUS_OFF)
        setParameters(48, 50)
        Notify(["Initialized contract successfully!"])
    return True

def setParameters(dividendForBankersPercentage, runningVaultPercentage):
    RequireWitness(Admin)
    currentRound = getCurrentRound()
    nextRound = Add(currentRound, 1)
    Require(Add(dividendForBankersPercentage, runningVaultPercentage) == 98)
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, nextRound), DIVIDEND_FOR_BANKERS_PERCENTAGE), dividendForBankersPercentage)
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, nextRound), RUNNING_VAULT_PERCENTAGE), runningVaultPercentage)
    Notify(["setParameters", nextRound, dividendForBankersPercentage, runningVaultPercentage])
    return True


def withdrawCommission():
    RequireWitness(Admin)
    commissionAmountToBeWithdraw = getCommission()
    Require(_transferONGFromContact(Admin, commissionAmountToBeWithdraw))
    # update commission amount
    Delete(GetContext(), COMMISSION_KEY)
    # update total ong amount
    Put(GetContext(), TOTAL_ONG_KEY, Sub(getTotalONG(), commissionAmountToBeWithdraw))
    Notify(["withdrawCommission", commissionAmountToBeWithdraw])
    return True

def migrateContract(code, needStorage, name, version, author, email, description, newReversedContractHash):
    RequireWitness(Admin)
    res = _transferONGFromContact(newReversedContractHash, getTotalONG())
    Require(res)
    if res == True:
        res = Migrate(code, needStorage, name, version, author, email, description)
        Require(res)
        Notify(["Migrate Contract successfully", Admin, GetTime()])
        return True
    else:
        Notify(["MigrateContractError", "transfer ONG to new contract error"])
        return False
############### for Admin to invoke End ##################
############### for Bankers to invoke Begin ##################
def bankerInvest(account, ongAmount):
    """
    invest ong to become a banker
    :param account:
    :return:
    """
    currentRound = getCurrentRound()
    if getRoundGameStatus(currentRound) == STATUS_OFF:
        newRound = Add(currentRound, 1)
        if currentRound == 0:
            RequireWitness(Admin)
        else:
            RequireWitness(account)
        if Add(getRunningVaultPercentage(newRound), getDividendForBankersPercentage(newRound)) != 98:
            setParameters(getDividendForBankersPercentage(currentRound), getRunningVaultPercentage(currentRound))
        Put(GetContext(), CURRENT_ROUND_KEY, newRound)
        Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, newRound), ROUND_STATUS), STATUS_ON)
        Notify(["startNewRound", newRound])

    _bankerInvest(account, ongAmount)

    return True

def _bankerInvest(account, ongAmount):
    currentRound = getCurrentRound()
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # "bankerInvest: Check witness failed!",
        Notify(["Error", 101])
        return False
    if ongAmount < bankerQuota:
        # bankerInvest: Please make sure you invest at least 1000 ONG to become a banker
        Notify(["Error", 103])
        return False
    # Require(_transferONG(account, ContractAddress, ongAmount))
    res = _transferONG(account, ContractAddress, ongAmount)
    if res == False:
        # bankerInvest: Transfer ONG to contract failed!
        Notify(["Error", 102])
        return False
    # try to update banker list
    bankersListKey = concatKey(concatKey(ROUND_PREFIX, currentRound), BANKERS_LIST_KEY)
    bankersListInfo = Get(GetContext(), bankersListKey)
    bankersList = []
    if bankersListInfo:
        bankersList = Deserialize(bankersListInfo)
        if not checkInBankerList(account, bankersList):
            bankersList.append(account)
            bankersListInfo = Serialize(bankersList)
            Put(GetContext(), bankersListKey, bankersListInfo)
    else:
        bankersList.append(account)
        bankersListInfo = Serialize(bankersList)
        Put(GetContext(), bankersListKey, bankersListInfo)

    dividendForBankersPercentage = getDividendForBankersPercentage(currentRound)
    runningVaultPercentage = getRunningVaultPercentage(currentRound)

    # add dividend to all the bankers, 48%
    dividend = Div(Mul(ongAmount, dividendForBankersPercentage), 100)

    # update profit per investment for bankers
    bankersInvestment = getBankersInvestment(currentRound)
    if bankersInvestment > 0:
        profitPerInvestmentForBankersToBeAdd = Div(Mul(dividend, MagnitudeForProfitPerSth), bankersInvestment)
        Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), PROFIT_PER_INVESTMENT_FOR_BANKERS_KEY), Add(profitPerInvestmentForBankersToBeAdd, getProfitPerInvestmentForBankers(currentRound)))
    else:
        # there will be no dividend
        dividend = 0
    # add running vault, 50%
    increasingRunVaultToBeAdd = Div(Mul(ongAmount, runningVaultPercentage), 100)
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), INCREASING_RUN_VAULT_KEY), Add(getIncreasingRunnVault(currentRound), increasingRunVaultToBeAdd))

    # update real time running vault
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), REAL_TIME_RUNNING_VAULT), Add(getRealTimeRunningVault(currentRound), increasingRunVaultToBeAdd))

    # treat the rest as the commission fee to admin, 2%
    restOngAmount = Sub(Sub(ongAmount, dividend), increasingRunVaultToBeAdd)
    # update the commission fee
    Put(GetContext(), COMMISSION_KEY, Add(getCommission(), restOngAmount))

    # update the account (or the banker) 's dividend and earning
    updateBankerDividend(account)
    updateBankerEarning(account)

    # update account's investment
    bankerKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(BANKER_INVEST_BALANCE_PREFIX, account))
    Put(GetContext(), bankerKey, Add(getBankerInvestment(currentRound, account), ongAmount))

    # update total bankers' investment
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), BANKERS_INVESTMENT_KEY), Add(bankersInvestment, ongAmount))

    # update total ong amount
    Put(GetContext(), TOTAL_ONG_KEY, Add(getTotalONG(), ongAmount))

    Notify(["bankerInvest", currentRound, account, ongAmount])

    return True


def bankerWithdrawDividend(account):
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # bankerWithdrawDividend: Check witness failed!,
        Notify(["Error", 201])
        return 0

    # update the banker's dividend and earning
    updateBankerDividend(account)

    bankerDividend = getBankerDividend(account)
    # Require(bankerDividend > 0)
    if bankerDividend <= 0:
        # bankerWithdrawDividend: Banker has no dividend
        Notify(["noDividend", account])
        return 0

    # Require(_transferONGFromContact(account, bankerDividend))
    res = _transferONGFromContact(account, bankerDividend)
    if res == False:
        # bankerWithdrawDividend: Transfer dividend to banker failed!
        Notify(["Error", 202])
        return 0

    Delete(GetContext(), concatKey(BANKER_DIVIDEND_BALANCE_PREFIX, account))
    # update the total ong amount
    Put(GetContext(), TOTAL_ONG_KEY, Sub(getTotalONG(), bankerDividend))

    Notify(["bankerWithdrawDividend", getCurrentRound(), account, bankerDividend])
    return bankerDividend


def bankerWithdrawEarning(account):
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # bankerWithdrawEarning: Check witness failed!,
        Notify(["Error", 301])
        return 0

    updateBankerEarning(account)
    # update the banker's earning
    bankerEarning = getBankerEarning(account)

    # RequireWitness(bankerEarning > 0)
    if bankerEarning <= 0:
        # banker's dividend is not greater than 0
        Notify(["noEarning", account])
        return 0

    # Require(_transferONGFromContact(account, bankerEarning))
    res = _transferONGFromContact(account, bankerEarning)
    if res == False:
        # bankerWithdrawEarning: Transfer ONG failed!
        Notify(["Error", 302])
        return 0

    Delete(GetContext(), concatKey(BANKER_EARNING_BALANCE_PREFIX, account))

    # update the total ong amount
    Put(GetContext(), TOTAL_ONG_KEY, Sub(getTotalONG(), bankerEarning))

    Notify(["bankerWithdrawEarning", getCurrentRound(), account, bankerEarning])
    return bankerEarning


def bankerWithdraw(account):
    dividend = bankerWithdrawDividend(account)
    earning = bankerWithdrawEarning(account)
    return Add(dividend, earning)

def bankerWithdrawBeforeExit(account):
    if CheckWitness(account) == False:
        # bankerWithdrawBeforeExit: Check witness failed!
        Notify(["Error", 401])
        return 0

    ongShareInRunningVault = getRunVaultShare(account)
    if ongShareInRunningVault <= 0:
        # bankerWithdrawBeforeExit: banker's dividend is not greater than 0
        Notify(["noShare", account])
        return 0
    currentRound = getCurrentRound()
    bankerBalanceInRunVault = getBankerBalanceInRunVault(currentRound, account)
    if getRoundGameStatus(currentRound) == STATUS_ON and bankerBalanceInRunVault > 0:
        # update the bankers' investment amount
        oldBankersInvestment = getBankersInvestment(currentRound)
        Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), BANKERS_INVESTMENT_KEY), Sub(oldBankersInvestment, getBankerInvestment(currentRound, account)))
        # delete the banker's investment balance
        Delete(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(BANKER_INVEST_BALANCE_PREFIX, account)))

    Require(_transferONGFromContact(account, ongShareInRunningVault))
    # update total ong
    Put(GetContext(), TOTAL_ONG_KEY, Sub(getTotalONG(), ongShareInRunningVault))
    # update real time run vault
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), REAL_TIME_RUNNING_VAULT), Sub(getRealTimeRunningVault(currentRound), ongShareInRunningVault))

    Notify(["bankerWithdraw", currentRound, account, ongShareInRunningVault])
    return ongShareInRunningVault

def bankerExit(account):
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # bankerExit: Check witness failed!,
        Notify(["Error", 501])
        return False

    currentRound = getCurrentRound()

    # withdraw the banker's dividend and earning
    dividend_earning = bankerWithdraw(account)

    ongShareInRunningVault = bankerWithdrawBeforeExit(account)

    totalWithdrawOng = Add(dividend_earning, ongShareInRunningVault)
    if totalWithdrawOng > 0:
        Notify(["bankerExit", currentRound, account, totalWithdrawOng])
    else:
        # bankerExit: No longer a banker
        Notify(["Error", 502])
        return True

    # mark the game as end if real time running vault is less than 1/10 of running vault
    realTimeRunVaultKey = concatKey(concatKey(ROUND_PREFIX, currentRound), REAL_TIME_RUNNING_VAULT)
    realTimeRunVault = getRealTimeRunningVault(currentRound)
    if realTimeRunVault < Div(getIncreasingRunnVault(currentRound), 10):
        # mark this round of game end
        Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), ROUND_STATUS), STATUS_OFF)
        # update profit per investment for bankers
        runVaultLeft = getRunningVault(currentRound)
        profitPerRuningVaultShareToBeAdd = 0
        if runVaultLeft > 0:
            profitPerRuningVaultShareToBeAdd = Div(Mul(realTimeRunVault, MagnitudeForProfitPerSth), runVaultLeft)
            Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), PROFIT_PER_RUNNING_VAULT_SHARE_KEY), Add(profitPerRuningVaultShareToBeAdd, getProfitPerRunningVaultShare(currentRound)))
        # update real time running vault
        Delete(GetContext(), realTimeRunVaultKey)
        Notify(["endCurrentRound", currentRound])
    return True
############### for Bankers to invoke End ##################
############### for players to invoke Begin ##################
def bet(account, ongAmount, number):
    """
    :param account:
    :param ongAmount:
    :param number:
    :return:
    """
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # bet: Check witness failed!
        Notify(["Error", 601])
        return False

    currentRound = getCurrentRound()

    # to prevent hack from other contract
    callerHash = GetCallingScriptHash()
    entryHash = GetEntryScriptHash()
    # Require(callerHash == entryHash)
    if callerHash != entryHash:
        # bet: Don't support bet method being invoked by another contract to prevent hacking
        Notify(["Error", 602])
        return False

    if getRoundGameStatus(currentRound) != STATUS_ON:
        # bet: Current round game ended, please wait for the starting of the next round game and try later
        Notify(["Error", 603])
        return False

    # make sure the contract has enough ong to pay to accont if account wins
    tryPayOutToWin = _calculatePayOutToWin(ongAmount, number)
    totalOngAmount = getTotalONG()
    realTimeRunVault = getRealTimeRunningVault(currentRound)

    # # Require(realTimeRunVault > tryPayOutToWin)
    if realTimeRunVault < Sub(tryPayOutToWin, ongAmount):
        # bet: Running pot/vault does not have enough asset to pay to the player, please try smaller bet
        Notify(["Error", 604])
        return False

    # Require(_transferONG(account, ContractAddress, ongAmount))
    res = _transferONG(account, ContractAddress, ongAmount)
    if res == False:
        # bet: Transfer ONG failed, please try later or again
        Notify(["Error", 605])
        return False

    # Require(number < 97)
    if number >=97:
        # bet: Please try to bet with a number less than 97
        Notify(["Error", 606])
        return False
    # Require(number > 1)
    if number <=1 :
        # bet: Please try to bet with a number greater than 1
        Notify(["Error", 607])
        return False

    theNumber = _rollANumber()
    payOutToWin = 0
    if theNumber < number:
        payOutToWin = tryPayOutToWin
        Require(_transferONGFromContact(account, payOutToWin))

        # update total ongAmount
        ongAmountToBeSub = Sub(payOutToWin, ongAmount)
        Put(GetContext(), TOTAL_ONG_KEY, Sub(totalOngAmount, ongAmountToBeSub))
        # update real time running vault
        realTimeRunVaultKey = concatKey(concatKey(ROUND_PREFIX, currentRound), REAL_TIME_RUNNING_VAULT)
        Put(GetContext(), realTimeRunVaultKey, Sub(realTimeRunVault, ongAmountToBeSub))
        realTimeRunVault = getRealTimeRunningVault(currentRound)
        # mark the game as end if real time running vault is less than 1/10 of running vault
        if realTimeRunVault <= Div(getIncreasingRunnVault(currentRound), 10):
            # mark this round of game end
            Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), ROUND_STATUS), STATUS_OFF)
            # update profit per investment for bankers
            runVaultLeft = getRunningVault(currentRound)
            if runVaultLeft > 0:
                profitPerRuningVaultShareToBeAdd = Div(Mul(realTimeRunVault, MagnitudeForProfitPerSth), runVaultLeft)
                Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), PROFIT_PER_RUNNING_VAULT_SHARE_KEY), Add(profitPerRuningVaultShareToBeAdd, getProfitPerRunningVaultShare(currentRound)))
            # update real time running vault
            Delete(GetContext(), realTimeRunVaultKey)
            Notify(["endCurrentRound", currentRound])
            return True
    else:
        # update total ong amount
        Put(GetContext(), TOTAL_ONG_KEY, Add(totalOngAmount, ongAmount))

        # update profit per investment for bankers
        runVaultLeft = getRunningVault(currentRound)
        if runVaultLeft > 0:
            profitPerRunNingVaultShareToBeAdd = Div(Mul(ongAmount, MagnitudeForProfitPerSth), runVaultLeft)
            Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), PROFIT_PER_RUNNING_VAULT_SHARE_KEY), Add(profitPerRunNingVaultShareToBeAdd, getProfitPerRunningVaultShare(currentRound)))

    Notify(["bet", currentRound, account, number, theNumber,ongAmount, payOutToWin])
    return True
############### for players to invoke End ##################
############### for all to pre-invoke Begin ##################
def getCurrentRound():
    return Get(GetContext(), CURRENT_ROUND_KEY)

def getDividendForBankersPercentage(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), DIVIDEND_FOR_BANKERS_PERCENTAGE))

def getRunningVaultPercentage(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), RUNNING_VAULT_PERCENTAGE))

def getTotalONG():
    return Get(GetContext(), TOTAL_ONG_KEY)

def getCommission():
    return Get(GetContext(), COMMISSION_KEY)

def getRoundGameStatus(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), ROUND_STATUS))

def getBankersInvestment(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), BANKERS_INVESTMENT_KEY))

def getIncreasingRunnVault(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), INCREASING_RUN_VAULT_KEY))

def getRunningVault(roundNumber):
    bankersInvestment = getBankersInvestment(roundNumber)
    return Div(Mul(bankersInvestment, getRunningVaultPercentage(roundNumber)), 100)


def getRealTimeRunningVault(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), REAL_TIME_RUNNING_VAULT))

def getBankersList(roundNumber, includeExitBankers):
    bankersListKey = concatKey(concatKey(ROUND_PREFIX, roundNumber), BANKERS_LIST_KEY)
    bankersListInfo = Get(GetContext(), bankersListKey)
    bankersList = []
    if bankersListInfo:
        bankersList = Deserialize(bankersListInfo)

    if includeExitBankers == True:
        return bankersList

    effectiveBankerList = []
    for banker in bankersList:
        if getBankerBalanceInRunVault(roundNumber, banker):
            effectiveBankerList.append(banker)
    return effectiveBankerList
############### for all to pre-invoke End ##################
############### for bankers to pre-invoke Begin ##################
def getBankerInvestment(roundNumber, account):
    return Get(GetContext(),concatKey(concatKey(ROUND_PREFIX, roundNumber), concatKey(BANKER_INVEST_BALANCE_PREFIX, account)))

def getBankerBalanceInRunVault(roundNumber, account):
    bankerInvestment = getBankerInvestment(roundNumber, account)
    return Div(Mul(bankerInvestment, getRunningVaultPercentage(roundNumber)), 100)

def getProfitPerInvestmentForBankers(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), PROFIT_PER_INVESTMENT_FOR_BANKERS_KEY))

def getProfitPerRunningVaultShare(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), PROFIT_PER_RUNNING_VAULT_SHARE_KEY))

def getBankersLastTimeUpdateDividendRound(account):
    return Get(GetContext(), concatKey(BANKER_LAST_TIME_UPDATE_DIVIDEND_ROUND_KEY, account))

def getBankersLastTimeUpdateEarnRound(account):
    return Get(GetContext(), concatKey(BANKER_LAST_TIME_UPDATE_EARNING_ROUND_KEY, account))
######################### Utility Methods Start #########################

def getRunVaultShare(account):
    currentRound = getCurrentRound()
    ongShareInRunningVault = 0

    # transfer his share in the running vault to his account
    bankerBalanceInRunVault = getBankerBalanceInRunVault(currentRound, account)
    runVault = getRunningVault(currentRound)
    realTimeRunVault = getRealTimeRunningVault(currentRound)
    if bankerBalanceInRunVault > 0 and realTimeRunVault > 0:
        ongShareInRunningVault = Div(Mul(Mul(bankerBalanceInRunVault, MagnitudeForProfitPerSth), realTimeRunVault), runVault)
        ongShareInRunningVault = Div(ongShareInRunningVault, MagnitudeForProfitPerSth)

    return ongShareInRunningVault

def getBankerEarning(account):
    currentRound = getCurrentRound()
    lastTimeUpdateEarnRound = getBankersLastTimeUpdateEarnRound(account)
    earningInStorage = Get(GetContext(), concatKey(BANKER_EARNING_BALANCE_PREFIX, account))
    unsharedProfitOngAmount = 0
    while (lastTimeUpdateEarnRound <= currentRound):
        profitPerRunVaultShare = getProfitPerRunningVaultShare(lastTimeUpdateEarnRound)
        profitPerRunVaultShareFromKey = concatKey(concatKey(ROUND_PREFIX, lastTimeUpdateEarnRound), concatKey(PROFIT_PER_RUNNING_VAULT_SHARE_FROM_KEY, account))
        profitPerRunVaultShareFrom = Get(GetContext(), profitPerRunVaultShareFromKey)
        unsharedProfitPerRunVaultShare = Sub(profitPerRunVaultShare, profitPerRunVaultShareFrom)

        bankerBalanceInRunVault = getBankerBalanceInRunVault(lastTimeUpdateEarnRound, account)
        if unsharedProfitPerRunVaultShare > 0 and bankerBalanceInRunVault > 0:
            unsharedProfit = Mul(bankerBalanceInRunVault, unsharedProfitPerRunVaultShare)
            unsharedProfitOngAmount = Add(unsharedProfitOngAmount, unsharedProfit)
        lastTimeUpdateEarnRound = Add(lastTimeUpdateEarnRound, 1)
    unsharedProfitOngAmount = Div(unsharedProfitOngAmount, MagnitudeForProfitPerSth)
    return Add(earningInStorage, unsharedProfitOngAmount)


def getBankerDividend(account):
    currentRound = getCurrentRound()
    lastTimeUpdateDividendRound = getBankersLastTimeUpdateDividendRound(account)
    dividendInStorage = Get(GetContext(), concatKey(BANKER_DIVIDEND_BALANCE_PREFIX, account))
    unsharedProfitOngAmount = 0
    while (lastTimeUpdateDividendRound <= currentRound):
        profitPerInvestmentForBankers = getProfitPerInvestmentForBankers(lastTimeUpdateDividendRound)
        profitPerInvestmentForBankerFromKey = concatKey(concatKey(ROUND_PREFIX, lastTimeUpdateDividendRound), concatKey(PROFIT_PER_INVESTMENT_FOR_BANKER_FROM_KEY, account))
        profitPerInvestmentForBankerFrom = Get(GetContext(), profitPerInvestmentForBankerFromKey)
        unsharedProfitPerInvestmentForBanker = Sub(profitPerInvestmentForBankers, profitPerInvestmentForBankerFrom)

        bankerInvestment = getBankerInvestment(lastTimeUpdateDividendRound, account)
        if unsharedProfitPerInvestmentForBanker != 0 and bankerInvestment != 0:
            unsharedProfit = Mul(unsharedProfitPerInvestmentForBanker, bankerInvestment)
            unsharedProfitOngAmount = Add(unsharedProfit, unsharedProfitOngAmount)
        lastTimeUpdateDividendRound = Add(lastTimeUpdateDividendRound, 1)

    unsharedProfitOngAmount = Div(unsharedProfitOngAmount, MagnitudeForProfitPerSth)
    return Add(dividendInStorage, unsharedProfitOngAmount)

def checkInBankerList(account, bankersList):
    for banker in bankersList:
        if account == banker:
            return True
    return False

def updateBankerDividend(account):
    currentRound = getCurrentRound()
    profitPerInvestmentForBankers = getProfitPerInvestmentForBankers(currentRound)
    profitPerInvestmentForBankerFromKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(PROFIT_PER_INVESTMENT_FOR_BANKER_FROM_KEY, account))
    profitPerInvestmentForBankerFrom = Get(GetContext(), profitPerInvestmentForBankerFromKey)
    unsharedProfitPerInvestment = Sub(profitPerInvestmentForBankers, profitPerInvestmentForBankerFrom)
    dividend = getBankerDividend(account)
    lastTimeUpdateDividendRound = getBankersLastTimeUpdateDividendRound(account)
    if unsharedProfitPerInvestment > 0 or lastTimeUpdateDividendRound != currentRound:
        Put(GetContext(), concatKey(BANKER_DIVIDEND_BALANCE_PREFIX, account), dividend)
        Put(GetContext(), concatKey(BANKER_LAST_TIME_UPDATE_DIVIDEND_ROUND_KEY, account), currentRound)
        Put(GetContext(), profitPerInvestmentForBankerFromKey, profitPerInvestmentForBankers)
    return True

def updateBankerEarning(account):
    currentRound = getCurrentRound()
    profitPerRunVaultShare = getProfitPerRunningVaultShare(currentRound)
    profitPerRunVaultShareFromKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(PROFIT_PER_RUNNING_VAULT_SHARE_FROM_KEY, account))
    profitPerRunVaultShareFrom = Get(GetContext(), profitPerRunVaultShareFromKey)
    unsharedProfitPerRunVaultShare = Sub(profitPerRunVaultShare, profitPerRunVaultShareFrom)
    earning = getBankerEarning(account)
    lastTimeUpdateEarnRound = getBankersLastTimeUpdateEarnRound(account)
    if unsharedProfitPerRunVaultShare > 0 or lastTimeUpdateEarnRound != currentRound:
        Put(GetContext(), concatKey(BANKER_EARNING_BALANCE_PREFIX, account), earning)
        Put(GetContext(), concatKey(BANKER_LAST_TIME_UPDATE_EARNING_ROUND_KEY, account), currentRound)
        Put(GetContext(), profitPerRunVaultShareFromKey, profitPerRunVaultShare)
    return True


def _calculatePayOutToWin(ongAmount, number):
    payOutToWin = Div(Mul(98, ongAmount), Sub(number, 1))
    return payOutToWin

def _rollANumber():
    blockHash = GetCurrentBlockHash()
    tx = GetScriptContainer()
    txhash = GetTransactionHash(tx)
    theNumber = abs(blockHash ^ txhash) % 100
    theNumber = Add(abs(theNumber), 1)
    return theNumber

def _transferONG(fromAcct, toAcct, amount):
    """
    transfer ONG
    :param fromacct:
    :param toacct:
    :param amount:
    :return:
    """
    RequireWitness(fromAcct)
    param = state(fromAcct, toAcct, amount)
    res = Invoke(0, ONGAddress, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False

def _transferONGFromContact(toAcct, amount):
    param = state(ContractAddress, toAcct, amount)
    res = Invoke(0, ONGAddress, 'transfer', [param])
    if res and res == b'\x01':
        return True
    else:
        return False

def concatKey(str1,str2):
    """
    connect str1 and str2 together as a key
    :param str1: string1
    :param str2:  string2
    :return: string1_string2
    """
    return concat(concat(str1, '_'), str2)
######################### Utility Methods End #########################

"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/Utils.py
"""
def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)


"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/SafeCheck.py
"""
def Require(condition):
    """
	If condition is not satisfied, return false
	:param condition: required condition
	:return: True or false
	"""
    if not condition:
        Revert()
    return True

def RequireScriptHash(key):
    """
    Checks the bytearray parameter is script hash or not. Script Hash
    length should be equal to 20.
    :param key: bytearray parameter to check script hash format.
    :return: True if script hash or revert the transaction.
    """
    Require(len(key) == 20)
    return True

def RequireWitness(witness):
    """
	Checks the transaction sender is equal to the witness. If not
	satisfying, revert the transaction.
	:param witness: required transaction sender
	:return: True if transaction sender or revert the transaction.
	"""
    Require(CheckWitness(witness))
    return True
"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/SafeMath.py
"""

def Add(a, b):
    """
	Adds two numbers, throws on overflow.
	"""
    c = a + b
    Require(c >= a)
    return c

def Sub(a, b):
    """
    Substracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    Require(a>=b)
    return a-b

def ASub(a, b):
    if a > b:
        return a - b
    if a < b:
        return b - a
    else:
        return 0

def Mul(a, b):
    """
    Multiplies two numbers, throws on overflow.
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    if a == 0:
        return 0
    c = a * b
    Require(c / a == b)
    return c

def Div(a, b):
    """
    Integer division of two numbers, truncating the quotient.
    """
    Require(b > 0)
    c = a / b
    return c

def Pwr(a, b):
    """
    a to the power of b
    :param a the base
    :param b the power value
    :return a^b
    """
    c = 0
    if a == 0:
        c = 0
    elif b == 0:
        c = 1
    else:
        i = 0
        c = 1
        while i < b:
            c = Mul(c, a)
            i = i + 1
    return c

def Sqrt(a):
    """
    Return sqrt of a
    :param a:
    :return: sqrt(a)
    """
    c = Div(Add(a, 1), 2)
    b = a
    while(c < b):
        b = c
        c = Div(Add(Div(a, c), c), 2)
    return c

