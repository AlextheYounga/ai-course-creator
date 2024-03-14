Our courses will have certain answerable components which will quiz the user. Questions should be challenging but not impossible. Questions should test the user's comprehension of the page material well. Most importantly, multiple choice questions should never, under any circumstances, have more than one correct answer. One answer should be correct, and the other three should be incorrect. Do not ever create a multiple choice question with more than one correct answer. Please use one of the following component types at random: 


- Multiple Choice
- Fill in the Blank
- True/False


While creating page material, please cleverly insert an answerable component somewhere in the page. Since our course content will be in markdown, and HTML can be written within markdown, please insert the component in the following HTML formats:

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

## True/False
<div id="answerable-multiple-choice">
    <p id="question">Is this true or false?</p>
    <select id="choices">
        <option id="correct-answer">True</option>
        <option>False</option>
    </select>
</div>


>NOTE: The correct choice should contain an id="correct-answer"