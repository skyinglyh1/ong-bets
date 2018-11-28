from boa.interop.Ontology.Contract import Migrate
from boa.interop.System.Storage import GetContext, Get, Put
from boa.interop.System.Runtime import CheckWitness, GetTime, Notify
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash, GetCallingScriptHash, GetEntryScriptHash
from boa.interop.Ontology.Native import Invoke
from boa.interop.Ontology.Runtime import GetCurrentBlockHash
from boa.builtins import ToScriptHash, state

# the script hash of this contract
ContractAddress = GetExecutingScriptHash()
ONGAddress = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02')
# E.T account
Admin = ToScriptHash("ARiYs54Kq9T5h3QY1xTyXGb9gsJ1TUbMB7")
# skyinglyh account
# Admin = ToScriptHash("AQf4Mzu1YJrhz9f3aRkkwSm9n3qhXGSh4p")
INITIALIZED = "INIT"
TOTAL_ONG_KEY = "totalONG"

def Main(operation, args):
    ############### for Admin to invoke Begin ##################
    if operation == "init":
        return init()
    if operation == "invest":
        if len(args) == 1:
            ongAmount = args[0]
            return invest(ongAmount)
        else:
            return False
    if operation == "withdraw":
        if len(args) == 1:
            ongAmount = args[0]
            return withdraw(ongAmount)
        else:
            return False
    if operation == "migrateContract":
        if len(args) != 9:
            return False
        account = args[0]
        code = args[1]
        needStorage = args[2]
        name = args[3]
        version = args[4]
        author = args[5]
        email = args[6]
        description = args[7]
        newReversedContractHash = args[8]
        return migrateContract(account, code, needStorage, name, version, author, email, description, newReversedContractHash)
    ############### for Admin to invoke Begin ##################

    ############### for players to invoke Begin ##################
    if operation == "bet":
        if len(args) == 3:
            account = args[0]
            ongAmount = args[1]
            number = args[2]
            return bet(account, ongAmount, number)
        else:
            return False
    ############### for players to invoke End ##################

    if operation == "getTotalONG":
        return getTotalONG()

    return False


def init():
    RequireWitness(Admin)
    inited = Get(GetContext(), INITIALIZED)
    if inited:
        Notify(["idiot admin, you have initialized the contract"])
        return False
    else:
        Put(GetContext(), INITIALIZED, 1)
        Put(GetContext(), TOTAL_ONG_KEY, 0)
        Notify(["Initialized contract successfully"])
    return True


def bet(account, ongAmount, number):
    """
    :param account:
    :param ongAmount:
    :param number:
    :return:
    """
    RequireWitness(account)
    # to prevent hack from other contract
    callerHash = GetCallingScriptHash()
    entryHash = GetEntryScriptHash()
    Require(callerHash == entryHash)

    # make sure the contract has enough ong to pay to accont if account wins
    tryPayOutToWin = _calculatePayOutToWin(ongAmount, number)
    totalOngAmount = getTotalONG()
    Require(totalOngAmount >= tryPayOutToWin)

    Require(_transferONG(account, ContractAddress, ongAmount))

    Require(number < 97)
    Require(number > 1)
    theNumber = _rollANumber()
    payOutToWin = 0
    if theNumber < number:
        payOutToWin = tryPayOutToWin
        Require(_transferONGFromContact(account, payOutToWin))
        ongAmountToBeSub = Sub(payOutToWin, ongAmount)
        Put(GetContext(), TOTAL_ONG_KEY, Sub(totalOngAmount, ongAmountToBeSub))
    else:
        Put(GetContext(), TOTAL_ONG_KEY, Add(totalOngAmount, ongAmount))

    Notify(["bet", account, number, theNumber,ongAmount, payOutToWin])

    return True


def invest(ongAmount):
    RequireWitness(Admin)
    Require(_transferONG(Admin, ContractAddress, ongAmount))
    Put(GetContext(), TOTAL_ONG_KEY, Add(getTotalONG(), ongAmount))
    Notify(["invest", ongAmount])
    return True

def withdraw(ongAmount):
    RequireWitness(Admin)
    Require(_transferONGFromContact(Admin, ongAmount))
    Put(GetContext(), TOTAL_ONG_KEY, Sub(getTotalONG(), ongAmount))
    Notify(["withdraw", ongAmount])
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


def getTotalONG():
    return Get(GetContext(), TOTAL_ONG_KEY)



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




"""
https://github.com/tonyclarking/python-template/blob/master/libs/Utils.py
"""
def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)


"""
https://github.com/tonyclarking/python-template/blob/master/libs/SafeCheck.py
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
SafeMath 
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

