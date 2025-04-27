# f(a) -> a + b env: [[b: 4], [+: fn]]
# f(5)
# (a) (a + b) env

def account(*params):
  balance = params[0]

  def deposit(amount):
    return balance + amount

  def withdraw(amount):
    return balance - amount

  def dispatch(action, param=""):
    # we need extract to be able to typecast the params /instantiate the child object/
    if(action == 'extract'):
      return params
    if(action == 'deposit'):
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

# print(credit_account(100)('balance'));

# Here's what we get when we want to check the account balance of a credit account:

# Traceback (most recent call last):
#   File "/home/spectrum/playground/functions/oopfp/lab.py", line 70, in <module>
#     print(credit_account(100)('balance'))
#           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/spectrum/playground/functions/oopfp/lab.py", line 52, in dispatch
#     sa_result = saccount(action, param)
#                 ^^^^^^^^^^^^^^^^^^^^^^^
#   File "/home/spectrum/playground/functions/oopfp/lab.py", line 37, in dispatch
#     savings_account(basic_account(action, param)('balance'))

# In this configuration, we are unable to delegate calculations to the parent
# that do not respond with a new account object. Here the case is with `balance`.
# The problem is that through delegation we always expect a new account.
# One thing we can do is to check if the result is an object and

def type_respecting_savings_account(balance):
  basic_account = account(balance)

  def dispatch(action, param=""):
    if(action == 'interest'):
      return balance * 0.2
    elif (action == 'deposit'):
      return type_respecting_savings_account(balance + 2 * param)
    else:
      basic_account_result = basic_account(action, param)

      if basic_account_result == basic_account:
        new_savings_account = \
          type_respecting_savings_account(basic_account(action, param)('balance'))
        return new_savings_account
      else:
        return basic_account_result

  return dispatch

def type_respecting_credit_account(balance):
  baccount = account(balance)
  saccount = type_respecting_savings_account(balance)

  def dispatch(action, param = ""):
    sa_result = saccount(action, param)

    if(sa_result == 'wat?'):
      ba_result = baccount(action, param)

      if(ba_result != 'wat?'):
        if ba_result == account:
          new_credit_account = \
            type_respecting_credit_account(baccount(action, param)('balance'))
          return new_credit_account
        else:
          return ba_result
      else:
        return f"unable to resolve {action}"
    else:
      if sa_result == type_respecting_savings_account:
        new_credit_account = \
          type_respecting_credit_account(saccount('balance'))
        return new_credit_account
      else :
        return sa_result

  return dispatch

print(type_respecting_credit_account(120)('balance'))

# This assumes the dependencies be of same _type_, or at least accept the args
def a_more_convenient_account_constructor(*args, dependencies = []):

  def dispatch(action, *params):
    # one by one instantiate the dependencies with the params
    # see if any of them can handle the action. Once one of them can
    # handle the action, return the result
    # if none of them can handle the action, return
    # - the last result
    # - something of your own

    for dep in dependencies:
      result = dep(*args)(action, *params)
      if result != 'wat?':
        if result == dep:
          # if the result is the same as the dependency, we need to
          # create a new instance of the dependency with the params
          return a_more_convenient_account_constructor(*dep('extract'))
        else:
          return result

    return 'wat?'


  return dispatch

print(a_more_convenient_account_constructor(320, dependencies=[type_respecting_savings_account, account])('deposit', 50)('balance'))

# misc

class A:
  def a(self):
    return 10

class B:
  def a(self):
    return 20

class C(A, B):
  pass

# print(C.mro())
