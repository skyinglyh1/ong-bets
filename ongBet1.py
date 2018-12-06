from boa.interop.Ontology.Contract import Migrate
from boa.interop.System.Storage import GetContext, Get, Put, Delete
from boa.interop.System.Runtime import CheckWitness, GetTime, Notify
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash, GetEntryScriptHash
from boa.interop.Ontology.Native import Invoke
from boa.interop.Ontology.Runtime import GetCurrentBlockHash
from boa.builtins import ToScriptHash, concat, state

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
BANKERS_START_KEY = "BankersStart"

ROUND_PREFIX = "RoundPrefix"
CURRENT_ROUND_KEY = "CurrentRound"
# ROUND_PREFIX + CURRENT_ROUND_KEY + ROUND_STATUS
ROUND_STATUS = "RoundInit"
# DIVIDEND_FOR_BANKERS_PERCENTAGE  -- to store 48
DIVIDEND_FOR_BANKERS_PERCENTAGE = "DividendForBankersPercentage"
# RUNNING_VAULT_PERCENTAGE -- to store 50
RUNNING_VAULT_PERCENTAGE = "RunningVaultPercentage"


# ROUND_PREFIX + CURRENT_ROUND_KEY + BANKERS_INVESTMENT_KEY -- total investment
BANKERS_INVESTMENT_KEY = "BankersInvestment"
# ROUND_PREFIX + CURRENT_ROUND_KEY + RUNNING_VAULT_KEY -- ong that has been added into the running vault
RUNNING_VAULT_KEY = "RunningVault"
# ROUND_PREFIX + CURRENT_ROUND_KEY + REAL_TIME_RUNNING_VAULT -- running vault except the earnings, ong that can be paid to the players
REAL_TIME_RUNNING_VAULT = "RealTimeRunningVault"
# ROUND_PREFIX + CURRENT_ROUND_KEY + PROFIT_PER_INVESTMENT_FOR_BANKERS_KEY
PROFIT_PER_INVESTMENT_FOR_BANKERS_KEY = "ProfitPerInvestmentForBankers"
PROFIT_PER_RUNNING_VAULT_SHARE_KEY = "ProfitPerRunningVaultShare"


# ROUND_PREFIX + CURRENT_ROUND_KEY + PROFIT_PER_INVESTMENT_FOR_BANKER_FROM_KEY + account
PROFIT_PER_INVESTMENT_FOR_BANKER_FROM_KEY = "G1"
PROFIT_PER_RUNNING_VAULT_SHARE_FROM_KEY = "G2"
# ROUND_PREFIX + CURRENT_ROUND_KEY + BANKER_INVEST_BALANCE_PREFIX + account -> ong that has been invested into this game by the banker(account)
BANKER_INVEST_BALANCE_PREFIX = "G3"
# ROUND_PREFIX + CURRENT_ROUND_KEY + BANKER_RUNING_VAULT_BALANCE_PREFIX + account -> shares that the banker(account) have in the running vault
BANKER_RUNING_VAULT_BALANCE_PREFIX = "G4"

# BANKER_LAST_TIME_UPDATE_DIVIDEND_ROUND_KEY + account  -- store the round number the banker last time updates his dividend
BANKER_LAST_TIME_UPDATE_DIVIDEND_ROUND_KEY = "BankerLastTimeUpdateDividendRound"
# BANKER_LAST_TIME_UPDATE_EARNING_ROUND_KEY + account  -- store the round number the banker last time updates his earning
BANKER_LAST_TIME_UPDATE_EARNING_ROUND_KEY = "BankerLastTimeUpdateEarningRound"

# ROUND_PREFIX + CURRENT_ROUND_KEY + BANKER_DIVIDEND_BALANCE_PREFIX + account -- store the account's dividend as a banker
BANKER_DIVIDEND_BALANCE_PREFIX = "G5"
# BANKER_DIVIDEND_BALANCE_PREFIX + account -- store the account's shared earning as a banker from the running vault
BANKER_EARNING_BALANCE_PREFIX = "G6"
# BANKER_WITHDRAWN_BALANCE_KEY + account -- store the account's withdrawn amount of ong
BANKER_WITHDRAWN_BALANCE_KEY = "G7"


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
    if operation == "setInitialInvest":
        if len(args) != 1:
            return False
        ongAmount = args[0]
        return setInitialInvest(ongAmount)
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
    if operation == "bankerWithdrawDividend":
        if len(args) != 1:
            return False
        account = args[0]
        return bankerWithdrawDividend(account)
    if operation == "bankerWithdrawEarning":
        if len(args) != 1:
            return False
        account = args[0]
        return bankerWithdrawEarning(account)
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
        return getDividendForBankersPercentage()
    if operation == "getRunningVaultPercentage":
        return getRunningVaultPercentage()
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
    ############### for all to pre-invoke End ##################
    ############### for bankers to pre-invoke Begin ##################
    if operation == "getBankerInvestment":
        if len(args) != 2:
            return False
        roundNumber = args[0]
        account = args[1]
        return getBankerInvestment(roundNumber, account)
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
    if operation == "getBankerBalanceInRunVault":
        if len(args) != 2:
            return False
        roundNumber = args[0]
        account = args[1]
        return getBankerBalanceInRunVault(roundNumber, account)

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
    return False

############### for Admin to invoke Begin ##################
def init():
    RequireWitness(Admin)
    inited = Get(GetContext(), INITIALIZED)
    if inited:
        Notify(["idiot admin, you have initialized the contract"])
        return False
    else:

        setParameters(48, 50)
        Notify(["Initialized contract successfully"])
    return True

def setParameters(dividendForBankersPercentage, runningVaultPercentage):
    RequireWitness(Admin)

    Put(GetContext(), DIVIDEND_FOR_BANKERS_PERCENTAGE, dividendForBankersPercentage)
    Put(GetContext(), RUNNING_VAULT_PERCENTAGE, runningVaultPercentage)
    Notify(["setParameters", dividendForBankersPercentage, runningVaultPercentage])
    return True

def startNewRound(ongAmount):
    RequireWitness(Admin)
    Put(GetContext(), CURRENT_ROUND_KEY, Add(getCurrentRound(), 1))
    setInitialInvest(ongAmount)
    Notify(["startNewRound", getCurrentRound()])

def setInitialInvest(ongAmount):
    RequireWitness(Admin)
    currentRound = getCurrentRound()

    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), ROUND_STATUS), STATUS_ON)
    bankerInvest(Admin, ongAmount)

    Notify(["setInitialInvest", currentRound, ongAmount])
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
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # "Check witness failed!",
        Notify(["BankerInvestErr", 101])
        return False

    currentRound = getCurrentRound()

    # Require(getRoundGameStatus(currentRound) == STATUS_ON)
    if getRoundGameStatus(currentRound) != STATUS_ON:
        # Please wait for the admin to set initial investment!
        Notify(["BankerInvestErr", 102])
        return False

    # Require(_transferONG(account, ContractAddress, ongAmount))
    res = _transferONG(account, ContractAddress, ongAmount)
    if res == False:
        # Transfer ONG failed!
        Notify(["BankerInvestErr", 103])
        return False

    dividendForBankersPercentage = getDividendForBankersPercentage()
    runningVaultPercentage = getRunningVaultPercentage()

    # add dividend to all the bankers, 48%
    dividend = Div(Mul(ongAmount, dividendForBankersPercentage), 100)

    # update profit per investment for bankers
    bankersInvestment = getBankersInvestment(currentRound)
    if bankersInvestment != 0:
        profitPerInvestmentForBankersToBeAdd = Div(Mul(dividend, MagnitudeForProfitPerSth), bankersInvestment)
        Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), PROFIT_PER_INVESTMENT_FOR_BANKERS_KEY), Add(profitPerInvestmentForBankersToBeAdd, getProfitPerInvestmentForBankers(currentRound)))
    else:
        # there will be no dividend
        dividend = 0
    # add running vault, 50%
    runningVaultToBeAdd = Div(Mul(ongAmount, runningVaultPercentage), 100)
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), RUNNING_VAULT_KEY), Add(getRunningVault(currentRound), runningVaultToBeAdd))

    # add running vault balance
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(BANKER_RUNING_VAULT_BALANCE_PREFIX, account)), Add(getBankerBalanceInRunVault(currentRound, account), runningVaultToBeAdd))
    # update real time running vault
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), REAL_TIME_RUNNING_VAULT), Sub(getRealTimeRunningVault(currentRound), runningVaultToBeAdd))

    # treat the rest as the commission fee to admin, 2%
    restOngAmount = Sub(Sub(ongAmount, dividend), runningVaultToBeAdd)

    # update the commission fee
    Put(GetContext(), COMMISSION_KEY, Add(getCommission(), restOngAmount))

    # update the account (or the banker) 's dividend
    updateBankerDividend(account)

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
        # "Check witness failed!",
        Notify(["BankerWithdrawDividendErr", 201])
        return False

    # # Require(getBankerInvestment(account) > 0)
    # if getBankerInvestment(account) <= 0:
    #     # "account is NOT a banker",
    #     Notify(["BankerWithdrawDividendErr", 202])
    #     return False
    updateBankerDividend(account)

    # update the banker's dividend
    bankerDividend = getBankerDividend(account)
    # Require(bankerDividend > 0)
    if bankerDividend <= 0:
        # banker's dividend is not greater than 0
        Notify(["BankerWithdrawDividendErr", 203])
        return False

    # Require(_transferONGFromContact(account, bankerDividend))
    res = _transferONGFromContact(account, bankerDividend)
    if res == False:
        # Transfer ONG failed!
        Notify(["BankerWithdrawDividendErr", 204])
        return False

    Delete(GetContext(), concatKey(BANKER_DIVIDEND_BALANCE_PREFIX, account))
    # update the total ong amount
    Put(GetContext(), TOTAL_ONG_KEY, Sub(getTotalONG(), bankerDividend))

    Notify(["bankerWithdrawDividend", account, bankerDividend])
    return True


def bankerWithdrawEarning(account):
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # "Check witness failed!",
        Notify(["BankerWithdrawEarningErr", 301])
        return False

    # # RequireWitness(getBankerInvestment(account) > 0)
    # if getBankerInvestment(account) <= 0:
    #     # "account is NOT a banker",
    #     Notify(["BankerWithdrawEarningErr", 302])
    #     return False

    updateBankerEarning(account)
    # update the banker's earning
    bankerEarning = getBankerEarning(account)

    # RequireWitness(bankerEarning > 0)
    if bankerEarning <= 0:
        # banker's dividend is not greater than 0
        Notify(["BankerWithdrawEarningErr", 303])
        return False

    # Require(_transferONGFromContact(account, bankerEarning))
    res = _transferONGFromContact(account, bankerEarning)
    if res == False:
        # Transfer ONG failed!
        Notify(["BankerWithdrawEarningErr", 304])
        return False

    Delete(GetContext(), concatKey(BANKER_EARNING_BALANCE_PREFIX, account))

    # update the total ong amount
    Put(GetContext(), TOTAL_ONG_KEY, Sub(getTotalONG(), bankerEarning))

    Notify(["bankerWithdrawEarning", account, bankerEarning])
    return True


def bankerWithdraw(account):
    bankerWithdrawDividend(account)
    bankerWithdrawEarning(account)
    return True


def bankerExit(account):
    # RequireWitness(account)
    if CheckWitness(account) == False:
        # "Check witness failed!",
        Notify(["BankerExitErr", 401])
        return False

    # # Require(getBankerInvestment(account) > 0)
    # if getBankerInvestment(account) <= 0:
    #     # "account is NOT a banker",
    #     Notify(["BankerExitErr", 402])
    #     return False

    currentRound = getCurrentRound()

    # withdraw the banker's dividend
    bankerWithdrawDividend(account)

    # withdraw the banker's earning
    bankerWithdrawEarning(account)

    # update the bankers total investment
    bankerBalanceInRunVault = getBankerBalanceInRunVault(currentRound, account)
    Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), BANKERS_INVESTMENT_KEY), Sub(getBankersInvestment(currentRound), bankerBalanceInRunVault))
    Delete(GetContext(), concatKey(BANKER_RUNING_VAULT_BALANCE_PREFIX, account))

    # update the banker's investment
    Delete(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(BANKER_INVEST_BALANCE_PREFIX, account)))

    Notify(["bankerExit", currentRound, account])
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
        # "Check witness failed!",
        Notify(["BetErr", 501])
        return False

    currentRound = getCurrentRound()

    # to prevent hack from other contract
    callerHash = GetCallingScriptHash()
    entryHash = GetEntryScriptHash()
    # Require(callerHash == entryHash)
    if callerHash == entryHash:
        # Don't support bet method being invoked by another contract to prevent hacking
        Notify(["BetErr", 502])
        return False
    
    if getRoundGameStatus(currentRound) != STATUS_ON:
        # current round game ended, please wait for the starting of the next round game and try later
        Notify(["BetErr", 507])
        return False

    # make sure the contract has enough ong to pay to accont if account wins
    tryPayOutToWin = _calculatePayOutToWin(ongAmount, number)
    totalOngAmount = getTotalONG()
    realTimeRunVault = getRealTimeRunningVault(currentRound)

    # Require(realTimeRunVault > tryPayOutToWin)
    if realTimeRunVault < tryPayOutToWin:
        # the contract does not have enough asset to pay to the player, please try smaller bet
        Notify(["BetErr", 503])
        return False

    # Require(_transferONG(account, ContractAddress, ongAmount))
    res = _transferONG(account, ContractAddress, ongAmount)
    if res == False:
        # Transfer ONG failed, please try later or again
        Notify(["BetErr", 504])
        return False


    # Require(number < 97)
    if number >=97:
        # please try to bet with a number less than 97
        Notify(["BetErr", 505])
        return False
    # Require(number > 1)
    if number <=1 :
        # please try to bet with a number greater than 1
        Notify(["BetErr", 506])
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
        if realTimeRunVault < Div(getRunningVault(currentRound), 10):
            # mark this round of game end
            Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), ROUND_STATUS), STATUS_OFF)
            # update profit per investment for bankers
            profitPerInvestmentForBankersToBeAdd = Div(Mul(realTimeRunVault, MagnitudeForProfitPerSth), getBankersInvestment(currentRound))
            Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), PROFIT_PER_INVESTMENT_FOR_BANKERS_KEY), Add(profitPerInvestmentForBankersToBeAdd, getProfitPerInvestmentForBankers(currentRound)))
            # update real time running vault
            Delete(GetContext(), realTimeRunVaultKey)
            Notify(["GameEnd!", currentRound])
            return False
    else:
        # update total ong amount
        Put(GetContext(), TOTAL_ONG_KEY, Add(totalOngAmount, ongAmount))

        # update profit per investment for bankers
        profitPerInvestmentForBankersToBeAdd = Div(Mul(ongAmount, MagnitudeForProfitPerSth), getBankersInvestment(currentRound))
        Put(GetContext(), concatKey(concatKey(ROUND_PREFIX, currentRound), PROFIT_PER_INVESTMENT_FOR_BANKERS_KEY), Add(profitPerInvestmentForBankersToBeAdd, getProfitPerInvestmentForBankers(currentRound)))

    Notify(["bet", currentRound, account, number, theNumber,ongAmount, payOutToWin])
    return True
############### for players to invoke End ##################
############### for all to pre-invoke Begin ##################
def getCurrentRound():
    return Get(GetContext(), CURRENT_ROUND_KEY)

def getDividendForBankersPercentage():
    return Get(GetContext(), DIVIDEND_FOR_BANKERS_PERCENTAGE)

def getRunningVaultPercentage():
    return Get(GetContext(), RUNNING_VAULT_PERCENTAGE)

def getTotalONG():
    return Get(GetContext(), TOTAL_ONG_KEY)

def getCommission():
    return Get(GetContext(), COMMISSION_KEY)

def getRoundGameStatus(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), ROUND_STATUS))

def getBankersInvestment(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), BANKERS_INVESTMENT_KEY))

def getRunningVault(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), RUNNING_VAULT_KEY))

def getRealTimeRunningVault(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), REAL_TIME_RUNNING_VAULT))
############### for all to pre-invoke End ##################
############### for bankers to pre-invoke Begin ##################
def getBankerInvestment(roundNumber, account):
    return Get(GetContext(),concatKey(concatKey(ROUND_PREFIX, roundNumber), concatKey(BANKER_INVEST_BALANCE_PREFIX, account)))

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
            unsharedProfitOngAmount = Add(Div(unsharedProfit, MagnitudeForProfitPerSth), unsharedProfitOngAmount)
        #     return Add(dividendInStorage, unsharedProfitOngAmount)
        # return Get(GetContext(), concatKey(BANKER_DIVIDEND_BALANCE_PREFIX, account))
        lastTimeUpdateDividendRound = Add(lastTimeUpdateDividendRound, 1)
    return Add(dividendInStorage, unsharedProfitOngAmount)

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
        if unsharedProfitPerRunVaultShare != 0 and bankerBalanceInRunVault != 0:
            unsharedProfitOngAmount = Mul(bankerBalanceInRunVault, unsharedProfitPerRunVaultShare)

        lastTimeUpdateEarnRound = Add(lastTimeUpdateEarnRound, 1)

    return Add(earningInStorage, unsharedProfitOngAmount)
    # profitPerRunVaultShare = getProfitPerRunningVaultShare()
    # profitPerRunVaultShareFromKey = concatKey(PROFIT_PER_RUNNING_VAULT_SHARE_FROM_KEY, account)
    # unsharedProfitPerRunVaultShare = Sub(profitPerRunVaultShare, Get(GetContext(), profitPerRunVaultShareFromKey))
    # earningInStorage = Get(GetContext(), concatKey(BANKER_EARNING_BALANCE_PREFIX, account))
    # bankerBalanceInRunVault = getBankerBalanceInRunVault(account)
    # if unsharedProfitPerRunVaultShare != 0 and bankerBalanceInRunVault != 0:
    #     earning = Mul(bankerBalanceInRunVault, unsharedProfitPerRunVaultShare)
    #     return Add(earningInStorage, earning)
    # return Get(GetContext(), concatKey(BANKER_EARNING_BALANCE_PREFIX, account))


def getBankerBalanceInRunVault(roundNumber, account):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), concatKey(BANKER_RUNING_VAULT_BALANCE_PREFIX, account)))

def getProfitPerInvestmentForBankers(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), PROFIT_PER_INVESTMENT_FOR_BANKERS_KEY))

def getProfitPerRunningVaultShare(roundNumber):
    return Get(GetContext(), concatKey(concatKey(ROUND_PREFIX, roundNumber), PROFIT_PER_RUNNING_VAULT_SHARE_KEY))

def getBankersLastTimeUpdateDividendRound(account):
    return Get(GetContext(), concatKey(BANKER_LAST_TIME_UPDATE_DIVIDEND_ROUND_KEY, account))

def getBankersLastTimeUpdateEarnRound(account):
    return Get(GetContext(), concatKey(BANKER_LAST_TIME_UPDATE_EARNING_ROUND_KEY, account))



######################### Utility Methods Start #########################
def updateBankerDividend(account):
    currentRound = getCurrentRound()
    profitPerInvestmentForBankers = getProfitPerInvestmentForBankers(currentRound)
    profitPerInvestmentForBankerFromKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(PROFIT_PER_INVESTMENT_FOR_BANKER_FROM_KEY, account))
    Put(GetContext(), profitPerInvestmentForBankerFromKey, profitPerInvestmentForBankers)
    Put(GetContext(), concatKey(BANKER_DIVIDEND_BALANCE_PREFIX, account), getBankerDividend(account))
    return True

def updateBankerEarning(account):
    currentRound = getCurrentRound()
    profitPerRunVaultShare = getProfitPerRunningVaultShare(currentRound)
    profitPerRunVaultShareFromKey = concatKey(concatKey(ROUND_PREFIX, currentRound), concatKey(PROFIT_PER_RUNNING_VAULT_SHARE_FROM_KEY, account))
    Put(GetContext(), profitPerRunVaultShareFromKey, profitPerRunVaultShare)
    Put(GetContext(), concatKey(BANKER_EARNING_BALANCE_PREFIX, account), getBankerEarning(account))
    return True


def _calculatePayOutToWin(ongAmount, number):
    payOutToWin = Div(Mul(98, ongAmount), Sub(number, 1))
    return payOutToWin

def _rollANumber():
    blockHash = GetCurrentBlockHash()
    theNumber = abs(blockHash) % 100
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
