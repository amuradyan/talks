# f(a) -> a + b env: [[b: 4], [+: fn]]
# f(5)
# (a) (a + b) env

def account(balance):
  def deposit(amount):
    return balance + amount

  def withdraw(amount):
    return balance - amount

  def dispatch(action, param=""):
    if (action == 'deposit'):
      return account(deposit(param))
    elif (action == 'withdraw'):
      return account(withdraw(param))
    elif (action == 'balance'):
      return balance
    else:
      print("wat?")

  return dispatch

print(account(50)('deposit', 500)('balance'))

def savings_account(balance):
  basic_account = account(balance)

  def dispatch(action, param=""):
    if (action == 'interest'):
      return balance * 0.2
    elif (action == 'deposit'):
      return savings_account(balance + 2 * param)
    elif (action == 'balance'):
      return balance
    else:
      return savings_account(basic_account(action, param)('balance'))

  return dispatch

print(savings_account(60)('deposit', 60)('interest'))
# print(account(160)('balance',10)) # --> 60
