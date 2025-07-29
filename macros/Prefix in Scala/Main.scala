import Prefix.*

def logPayment(payment: String): String = {
  val currency  = s"${payment(0)}${payment(1)}${payment(2)}"
  val amount    = payment.drop(3).toDouble
  val timestamp = System.currentTimeMillis()
  s"$timestamp: $amount paid in $currency"
}

extension (inline ctx: StringContext) inline def prefix(): Int = Prefix.prefix(ctx)

@main def run(): Unit =
  println("Generic code example")
  println(logPayment("USD123.45"))
  println(logPayment("EUR678.90"))
  println

  println("Macro code example")
  println(prefix"+ 2 5 9")
  println(prefix"* 3 4 2")

  println(prefix"+ 5 5" + prefix"- 10 5")
