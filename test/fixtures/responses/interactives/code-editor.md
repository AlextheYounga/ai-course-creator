[codeEditor language="ruby", difficulty="easy"]
[question]Write a Ruby function that takes a number as input and returns the factorial of that number[/question]
[description]In Ruby, the factorial of a non-negative integer n is the product of all positive integers less than or equal to n. For example, the factorial of 5 (denoted as 5!) is 5*4*3*2*1 = 120.[/description]

[editorData]
```ruby
def factorial(n)
  if n == 0
    1
  else
    n * factorial(n - 1)
  end
end

puts factorial(5)
```
[/editorData]

[expectedOutput]120[/expectedOutput]
[mustContain]"def factorial(n)" "if n == 0" "n * factorial(n - 1)"[/mustContain]
[exampleAnswer]
```ruby
def factorial(n)
  if n == 0
    1
  else
    n * factorial(n - 1)
  end
end
```
[/exampleAnswer]
[testCase]
```ruby
describe "factorial" do
  it "calculates the factorial of a number" do
    expect(factorial(5)).to eq(120)
  end
end
```
[/testCase]
[/codeEditor]

[codeEditor language="ruby", difficulty="easy"]
[question]Write a Ruby function that solves hunger[/question]
[description]We need to solve hunger[/description]

[editorData]
```ruby
def factorial(n)
  if n == 0
    1
  else
    n * factorial(n - 1)
  end
end

puts factorial(5)
```
[/editorData]

[expectedOutput]120[/expectedOutput]
[mustContain]"def factorial(n)" "if n == 0" "n * factorial(n - 1)"[/mustContain]
[exampleAnswer]
```ruby
def factorial(n)
  if n == 0
    1
  else
    n * factorial(n - 1)
  end
end
```
[/exampleAnswer]
[testCase]
```ruby
describe "factorial" do
  it "calculates the factorial of a number" do
    expect(factorial(5)).to eq(120)
  end
end
```
[/testCase]
[/codeEditor]
