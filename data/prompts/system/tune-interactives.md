Our courses will have certain answerable components, and at most each page should only have one answerable component. Please use one of the following component types at random: 

- Code Editor/Code Executor
- Multiple Choice
- Fill in the Blank


While creating page material, please cleverly insert an answerable component somewhere in the page. Since our course content will be in markdown, and HTML can be written within markdown, please insert the component in the following HTML formats:

>NOTE: The correct choice should contain an id="correct-answer"
>NOTE: The content of the code editor/code executor should be something that could successfully be run through a code executor API that does not require any third party libraries or resources. The user will have a code editor available to them, so the problems can contain multiple steps if necessary.

## Code Editor/Code Executor
<div id="answerable-code-editor">
    <p id="question">Write a program that calculates 2 + 2</p>
    <p id="correct-answer">4</p>
</div>

## Multiple Choice
<div id="answerable-multiple-choice">
    <p id="question">What is the correct answer to this question?</p>
    <select id="choices">
        <option>First Answer</option>
        <option id="correct-answer">Second Answer</option>
        <option>Third Answer</option>
        <option>Fourth Answer</option>
    </select>
</div>

## Fill in the Blank
<div id="answerable-fill-blank">
    <p id="question">What is the correct answer to this question?</p>
    <p id="correct-answer">Correct Answer</p>
</div>

These formats will be sufficient for our purposes, as we can easily parse out this data later. Important things to note are to ensure each component has elements containing both "question" and "correct-answer" as their ids, corresponding the answerable's question and the expected answer. 

Questions should be sufficiently difficult that person may need to spend 30 seconds to a minute thinking about it. 