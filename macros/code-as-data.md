# Code as data

Our systems deal with ideas from different domains, and sometimes they need to speak the language of a peer system, like a database or and AI agent. The closer our programming systems close the gap between those languages - the better.

This can be addressed in many ways through our programming languages. One way of doing this is going full native with domain specific languages, like [SQL](https://en.wikipedia.org/wiki/SQL) or [LilyPond](https://lilypond.org/) or [regex](https://en.wikipedia.org/wiki/Regular_expression).

```sql
SELECT name, position
FROM employees
WHERE acting = true
```

```lilypond
% The Nokia tune from Gran Vals by Tarrega

\relative c'' {
  \key a \major
  \time 3/4

  e8 d | fis4 gis | cis,8 b d4 e | b8 a cis4 e | a,2. |
}
```

```regex
^\(\d{3}\)\s\d{3}-\d{4}$ ............. (matches phone numbers like (123) 456-7890)
```

Other ways to bridge the gap are by baking in a specific domain like [Scala](https://docs.scala-lang.org/) did with [XML](https://en.wikipedia.org/wiki/XML), or allow certain tricks via syntax sugar, like the builder pattern in Scala.

```scala
// XML literals

import scala.xml._

...
val company = "Acme Inc."

val employee =
  <employee company={company}>
    <name>Jane Smith</name>
    <position>Developer</position>
    <active>true</active>
  </employee>
...
```

```scala
// The builder pattern

import darling.{Mail, send}

def main(args: Array[String]) {
  ...
  send a new Mail
    from "leia@gmail.com"
    to "kenobi3318@wherever.io"
    withSubject "Help"
    andMessage "Help me, Obi-Wan Kenobi. You're my only hope."
    darling
  ...
}
```

Yet another approach is to go for a *general* language with syntactic extension capabilities. The latter can be a powerful tool and is achieved with what's commonly known as macros - actions that are taken at compile time and can be used to manipulate code.

These are two ways one can interact with a database in Scala.

```scala
// SQL : UPDATE person SET age = 30 WHERE name = 'John Doe'

// SQL interaction with [dooby](https://typelevel.org/doobie/index.html)
def updatePerson(name: String, age: Int): Boolean =
  ...
  sql"UPDATE person SET age = $age WHERE name = $name"
    .unsafeRunSync()
  ...

// ... and plain JDBC
def updatePerson(name: String, age: Int): Boolean =
  ...
  val stmt = conn.prepareStatement("update person set age = ? where name = ?")
  stmt.setInt(1, age)
  stmt.setString(2, name)
  stmt.executeUpdate()
  stmt.close()
  ...
```

Different languages provide different mechanics to do such things making the feature more or less wieldy. Let's look at how this is done in Scala and Clojure. First we'll write a simple function to parse a payment string into a log.

```scala
def logPayment(payment: String): String = {
  val currency  = s"${payment(0)}${payment(1)}${payment(2)}"
  val amount    = payment.drop(3).toDouble
  val timestamp = System.currentTimeMillis()
  s"$timestamp: $amount paid in $currency"
}
```

```clojure
(defn log-payment
  "Generates the log entry message for a payment"
  [payment]
  (let [currency (str (first payment) (second payment) (nth payment 2))
        amount (Double/parseDouble (reduce str "" (drop 3 payment)))
        timestamp (System/currentTimeMillis)]
    (str timestamp ": " amount " paid in " currency)))
```

Both cases are easy to read and write. Now let's look at how we can achieve something with macros. In particular, let's look at how we can introduce a new syntax for arithmetic operations.

Below is a Scala macro that that allows us to do /prefix notation/ arithmetics like so - `(+ 1 2 (- 5 6) (* 2 2))`.

```scala
// Prefix arithmetics in Scala

object Prefix:

  inline def prefix(inline ctx: StringContext): Int =
    ${ prefixImpl('ctx) }

  private def calculate(op: String, args: List[Int]): Int =
    op match
      case "+" => args.sum
      case "*" => args.product
      case "-" => args.reduce(_ - _)
      case "/" => args.reduce(_ / _)
      case _   =>
        throw new IllegalArgumentException(s"Unknown operator: $op")

  private def prefixImpl(ctxExpr: Expr[StringContext])(using Quotes): Expr[Int] =
    import quotes.reflect.*

    ctxExpr match
      case '{ StringContext(${ Expr(parts) }*) } =>
        val tokens = parts.head.split("\\s+").toList
        tokens match
          case op :: args =>
            val ints   = args.map(_.toInt)
            val result = calculate(op, ints)
            Expr(result)
          case Nil        =>
            report.error("Empty expression")
            Expr(0)
      case _                                     =>
        report.error("Expected a literal string")
        Expr(0)

...

// Usage

import Prefix.*
val result = prefix"+ 2 5 9" // result = 16
```

It can be thought of as two-part thingie:

- `calculate` - to evaluate the expression
- `prefix` - to do provide the machinery. `inline` is used to instruct the compiler to evaluate the expression at compile time.

Notice how the code is different from the *casual* payment log example. The `prefix` macro is a bit more verbose, it uses `inline`-s and `quote`-s and operates on `Expr`-s in `Context`-s. One has to go out out of their everyday Scala code to do such things.

Now, let's look at a similar example in Clojure. Here is how we can introduce infix arithmetics in a prefix notation language:

```clojure
;; Infix arithmetics in Clojure

(defn process-tokens [tokens]
  (let [first-num (first tokens)
        op (second tokens)
        second-num (nth tokens 2)
        remaining (drop 3 tokens)]
    (if (empty? remaining)
      (list op first-num second-num)
      (list op first-num
            (process-tokens (cons second-num remaining))))))

(defmacro infix
  "Interprets infix expressions with multiple operands"
  [infixed-expression]
  (process-tokens (seq infixed-expression)))

(infix ((infix (1 + 2)) * 4 / 5))
```

Here, the code is rather short. Just like the payment log operates on a list of characters, the macro operates on a list of arithmetic expression. The code is mostly the same, with the exception of `defmacro` to instruct the interpreter to treat the function as a macro. That's possible because Clojure is a Lisp, and Lisps treat code as data. This means that the code itself is a data structure, and we can manipulate it as we would an ordinary list.

Scala code looks like a text, it's readable ok, but it does not quite resemble a data structure. In fact, the only data structure it resembles is a string of characters, and that is not the most convenient representation to do operations with. In order to evaluate and\or manipulate it Scala turns it into a tree, where each token in the string is marked and placed appropriately. This is done by the compiler and hidden from the user. The tree is then traversed and evaluated. This means that what we will be manipulating is not the original string, but a tree representation of it.

Such traits simplify domain specific language creation, helping us to bridge the gap between our programming language and the domain.
