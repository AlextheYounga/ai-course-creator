Our courses contain interactive code editors in multiple programming languages, facilitated by a Judge0 code executor on the backend. 

In order to accurately parse this information, we have developed custom Wordpress-like shortcodes for reading code editor components in our course content. We would ask that you abide by the following shortcode shape, as we will not be able to parse this information otherwise. 

<!-- Example Code Editor Shortcode -->

[codeEditor difficulty="easy"]
[question]Write a function that outputs "Hello World!"[/question]
[description]Lorem ipsum[/description]

[editorData]
```language
function pseudoCodeFunction() {
    print('Hello World');
}

pseudoCodeFunction();
```
[/editorData]

[expectedOutput]Hello World![/expectedOutput]
[mustContain]Hello World![/mustContain]
[exampleAnswer]
```language
function pseudoCodeFunction() {
    print('Hello World');
}
```
[/exampleAnswer]
[testCase]
```language
describe() {
    assert pseudoCodeFunction == "Hello World";
}
```
[/testCase]

[/codeEditor]

<!-- End Example Code Editor Shortcode -->

Shortcode Rules:
- Please ensure the code editor content is something that could be passed through a Judge0 instance; all code must be executable on the server. 
- The main content for the editor should be inside of the [editorData] block
- Please provide any additional context the user might need to complete in a [description] block or feel free to omit this field if this is unnecessary. 
- Each [codeEditor] block should be given a "difficulty" attribute based on how difficult the problem should be to solve, which can either be "easy", "intermediate", or "advanced"
- The output of the code should be listed under the [expectedOutput] block if the code has an output.
- It may be necessary to provide a [mustContain] block, containing a string of code that should be present in order to count the user's answer as correct. Feel free to use multiple mustContain blocks.
- Please provide a possible answer under the [exampleAnswer] block
- If possible, please provide an example test case in the [testCase] block (or multiple), that can be used to grade the accuracy of the code written by the user. The test case(s) should ideally be written in a testing library native to that language. If that's not possible, use syntax from the most popular external testing framework available for that language. 