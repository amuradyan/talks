# Code as data

A while ago I was having a coffee with a friend, and since I was just getting into Lisps, I buzzed his ears off with the idea of *code-as-data* and how awesome it is. I was so exited about it, that he proposed I come and give a talk to his students on the topic. Below is the more coherent version of what was in that talk. You may find it one-sided, and rightly so, since most examples are in Scala, but that's because I've been doing Scala for the past few years and the ideas translate easily to other languages, so no harm there. For the Lisp, I chose Clojure. These two also play together since both provide JVM interop.

## Polyglot systems

An average software system, written in some programming language, usually deals with ideas from different domains, and often it needs to communicate to a peer system, like a database or AI agent, to delegate certain tasks. Those peer systems come with their own languages of all shapes and colors.

Take a look at the languages below, that allow us to manipulate data /[SQL](https://en.wikipedia.org/wiki/SQL)/, write music /[LilyPond](https://lilypond.org/)/ or match strings /[regex](https://en.wikipedia.org/wiki/Regular_expression)/:

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

Did you note how different they are in terms of both syntax and semantics? The smoother our programming languages bridge these gaps - the better. As it is often the case in software engineering, this can be achieved in many ways.

One way to bridge such gaps is to bake one language into another, like [Scala](https://docs.scala-lang.org/) did with [XML](https://en.wikipedia.org/wiki/XML):

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

Alternatively, we can design our languages in a way that allows certain tricks via syntax sugar, like the builder pattern in Scala making use of unary method calls on objects.

```scala
// The builder pattern

import darling.{Mail, send}

def main(args: Array[String]) {
  ...
  send a new Mail
    from "leia@gmail.com"
    to "kenobi57@wherever.io"
    withSubject "Help"
    andMessage "Help me, Obi-Wan Kenobi. You're my only hope."
    darling
  ...
}
```

Yet another approach is to go for a *general* language with syntactic extension capabilities. The latter can be a powerful tool and is achieved with what's commonly known as **macros** - actions that are taken at compile time and can be used to manipulate the code itself.

Before we dive in though, we'll take a step back and look at another example. Here are two ways one can interact with a database in Scala.

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
  val stmt = conn.prepareStatement("UPDATE person SET age = ? WHERE name = ?")
  stmt.setInt(1, age)
  stmt.setString(2, name)
  stmt.executeUpdate()
  stmt.close()
  ...
```

As you can see, the first version is less mechanical, and allows passing values from Scala to SQL via ordinary string interpolation rather than a dedicated API. All that is enabled by the `sql` prefixing the SQL string, implemented as a **macro**.

## Enter the macros

Different languages provide different mechanics to do such things, making the macros more or less wieldy. Let's look at how this is done in Scala and Clojure. First we'll write a simple function to parse a payment string into a log. The function assumes the payment info to be in the form of a three letter currency code followed by the amount, that can be a decimal, e.g. *USD12.34*, *AMD14.7* or *CAD78.96*. For the latter payment, the log string produced will be `2025-07-28T22:07:26.266675985: 78.96 paid in CAD`.

```scala
// "Generates the log entry message for a payment"
def logPayment(payment: String): String = {
  val currency  = s"${payment(0)}${payment(1)}${payment(2)}"
  val amount    = payment.drop(3).toDouble
  val timestamp = java.time.LocalDateTime.now

  s"$timestamp: $amount paid in $currency"
}
```

```clojure
(defn log-payment
  "Generates the log entry message for a payment"
  [payment]
  (let [currency (str (first payment) (second payment) (nth payment 2))
        amount (Double/parseDouble (reduce str "" (drop 3 payment)))
        timestamp (java.time.LocalDateTime/now)]
    (str timestamp ": " amount " paid in " currency)))
```

Both cases are easy to read and write, right? The are almost identical. Now let's look at how we can achieve something with macros. In particular, let's look at how we can introduce a new syntax for arithmetic operations.

Below is a Scala macro that that allows us to do /prefix notation/ arithmetics like so - `(+ 1 2 (- 5 6) (* 2 2))`.

```scala
// Prefix arithmetics in Scala
object Prefix:

  inline def prefix(inline ctx: StringContext): Int =
    ${ prefixImpl('ctx) }

  private def prefixImpl(ctxExpr: Expr[StringContext])(using Quotes): Expr[Int] =
    import quotes.reflect.*

    ctxExpr match
      case '{ StringContext(${ Expr(parts) }*) } =>
        val tokens = parts.head.split("\\s+").toList
        tokens match
          case op :: args =>
            val numbers = args.map(_.toInt)
            val result  = calculate(op, numbers)
            Expr(result)
          case Nil        =>
            report.error("Empty expression")
            Expr(0)
      case _                                     =>
        report.error("Expected a literal string")
        Expr(0)

  private def calculate(op: String, args: List[Int]): Int =
    op match
      case "+" => args.sum
      case "*" => args.product
      case "-" => args.reduce(_ - _)
      case "/" => args.reduce(_ / _)
      case _   =>
        throw new IllegalArgumentException(s"Unknown operator: $op")

// Usage from another file

import Prefix.*

print(prefix"+ 2 5 9") // 16
```

The Scala implementation can be thought of as a two-part thingie:

- `prefix` and `prefixImpl` - these handle the machinery. `inline` is used to instruct the compiler to evaluate the expression at compile time.
- `calculate` - actually evaluates the expression

Notice how the code is different from the *casual* payment log example. The `prefix` macro is a bit more verbose, it uses `inline`-s and `quote`-s and operates on `Expr`-s in `Context`-s. One has to go out of their *day-to-day* Scala code to implement such a thing.

Now, let's try and implement something similar in Clojure - infix arithmetics in a prefix notation language:

```clojure
;; Infix arithmetics in Clojure

(defn process-tokens [tokens]
  ""
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

Here, the code is much shorter. Just like the payment log operates on a list of characters, the macro operates on a list of arithmetic expression. The code is mostly the same, with the exception of `defmacro` to instruct the interpreter to treat the function as a macro. That's possible because Clojure is a Lisp, and Lisps treat code as data. This means that the code itself is a data structure, and we can manipulate it as we would an ordinary list.

Scala code looks like a text, it's readable ok, but it does not quite resemble a data structure. In fact, the only data structure it resembles is a string of characters, and that is not the most convenient representation to do operations with. In order to evaluate and\or manipulate it Scala turns it into a tree, where each token in the string is marked and placed appropriately. This is done by the compiler and hidden from the user. The tree is then traversed and evaluated. This means that what we will be manipulating is not the original string, but a tree representation of it.

Such traits simplify domain specific language creation, helping us to bridge the gap between our programming language and the domain.
