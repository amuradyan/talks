# f(a) -> a + b env: [[b: 4], [+: fn]]
# f(5)
# (a) (a + b) env

def account(balance):
  def deposit(amount):
    return balance + amount

  def withdraw(amount):
    return balance - amount

  def dispatch(action, param=""):
    if(action == 'deposit'):
      return account(deposit(param))
    elif (action == 'withdraw'):
      return account(withdraw(param))
    elif (action == 'balance'):
      return balance
    else:
      print("wat?")
      return "wat?"

  return dispatch

print(account(50)('deposit', 500)('balance'))

def savings_account(balance):
  basic_account = account(balance)

  def dispatch(action, param=""):
    if(action == 'interest'):
      return balance * 0.2
    elif (action == 'deposit'):
      return savings_account(balance + 2 * param)
    else:
      new_savings_account = \
        savings_account(basic_account(action, param)('balance'))
      return new_savings_account

  return dispatch

print(savings_account(60)('deposit', 60)('interest'))

def credit_account(balance):
  baccount = account(balance)
  saccount = savings_account(balance)

  def dispatch(action, param = ""):
    if(action == balance):
      return balance
    else:
      sa_result = saccount(action, param)

      if(sa_result == 'wat?'):
        ba_result = baccount(action, param)

        if(ba_result != 'wat?'):
          new_credit_account = \
            credit_account(ba_result('balance'))
          return new_credit_account
        else:
          return f"unable to resolve {action}"
      else:
        new_credit_account = \
          credit_account(sa_result('balance'))
        return new_credit_account

  return dispatch

print(credit_account(100)('balance'))

# print(account(160)('balance',10)) # --> 60

class A:
  def a(self):
    return 10

class B:
  def a(self):
    return 20

class C(A, B):
  pass

# print(C.mro())
