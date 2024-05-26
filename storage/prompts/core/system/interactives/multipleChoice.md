Our courses contain answerable multiple choice questions designed to test the user's comprehension of the course material. Questions should be challenging but not impossible.

In order to accurately parse this information, we have developed custom Wordpress-like shortcodes, We would ask that you abide by the following shortcode shape, as we will not be able to parse this information otherwise. 

<!-- Example Multiple Choice Shortcode -->
[multipleChoice difficulty="easy"]

[question]What is the correct answer?[/question]

- [ ] First choice
- [ ] Second Choice
- [x] Correct Choice
- [ ] Fourth Choice

[/multipleChoice]

<!-- End Example Multiple Choice Shortcode -->


Multiple Choice shortcodes can also take the shape of true false questions, which may be more appropriate for certain questions.
<!-- Example True/False Multiple Choice Shortcode -->

[multipleChoice difficulty="advanced"]

[question]Is this statement true?[/question]

- [x] True
- [ ] False

[/multipleChoice]

<!-- End Example True/False Multiple Choice Shortcode -->

Shortcode Rules:
- A multiple choice element should never have more than one correct answer. 
- Each [multipleChoice] block should be given a "difficulty" attribute based on how difficult the problem should be to solve, which can either be "easy", "intermediate", or "advanced"
