# f(a) -> a + b env: [[b: 4], [+: fn]]
# f(5)
# (a) (a + b) env

def account(balance):
  def deposit(amount):
    return balance + amount

  def withdraw(amount):
    return balance - amount

  def dispatch(action, param=""):
    if action == 'id':
      return 'basic_account'
    elif action == 'extract':
      return balance
    elif(action == 'deposit'):
      return account(deposit(param))
    elif (action == 'withdraw'):
      return account(withdraw(param))
    elif (action == 'balance'):
      return balance
    else:
      return "wat?"

  return dispatch

print(account(50)('deposit', 500)('balance'))

def savings_account(balance):
  basic_account = account(balance)

  def dispatch(action, param=""):
    if action == 'id':
      return 'savings_account'
    elif(action == 'interest'):
      return balance * 0.2
    elif (action == 'deposit'):
      return savings_account(balance + 2 * param)
    else:
      basic_account_result = \
        basic_account(action, param)

      if callable(basic_account_result) and basic_account_result('id') == account('id'):
        return savings_account(basic_account_result('balance'))
      else:
        return basic_account_result

  return dispatch

print(savings_account(60)('deposit', 60)('interest'))

def credit_account(balance):
  baccount = account(balance)
  saccount = savings_account(balance)

  def dispatch(action, param = ""):
    if action == 'id':
      return 'credit_account'
    elif(action == 'balance'):
      return balance
    else:
      sa_result = saccount(action, param)

      if(sa_result == 'wat?'):
        ba_result = baccount(action, param)

        if(ba_result != 'wat?'):
          if callable(ba_result) and ba_result('id') == baccount('id'):
            return credit_account(ba_result('balance'))
          else:
            return ba_result
        else:
          return f"unable to resolve {action}"
      else:
        if callable(sa_result) and sa_result('id') == saccount('id'):
          return credit_account(sa_result('balance'))
        else:
          return sa_result

  return dispatch

print(credit_account(100)('deposit', 20)('balance'))

# print(account(160)('balance',10)) # --> 60

def convenient_account(balance, dependencies=[]):
  def own_dispatch():
    pass

  def dispatch(action, params=''):
    # one by one instantiate the dependencies with the args
    # see if any of them can handle the action. Once one of them can
    # handle the action, return the result
    # if none of them can handle the action, return
    # - the last result
    # - something of your own
    for dependency in dependencies:
      dep_result = dependency(balance)(action, params)
      if dep_result != 'wat?':
        if callable(dep_result) and dep_result('id') == dependency('id'):
          state = dep_result('extract')
          return convenient_account(state, dependencies)
        else:
          return dep_result

  return dispatch

convenient_account(100, [account, savings_account])('deposit', 20)('balance')

class A:
  def a(self):
    return 10

class B:
  def a(self):
    return 20

class C(A, B):
  pass

# print(C.mro())

# print(5 == 5)

# f1 = lambda x: x + 1
# f2 = lambda x: x + 1

# def ff(a):
#   def f(b):
#     return a + b

#   return f

# ff1 = ff(1)
# ff2 = ff(1)

# print(f1 == f2)

# print(ff1 == ff2)
