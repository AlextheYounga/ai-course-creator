Using the provided list of required skills for mastery of {topic}, please create an outline for a series of 10 small courses as you think are needed that can ideally be consumed in less than two hours. Each course should have at least two modules. Reorganize the items as needed, and try to make each course relatively independent. Make sure each chapter concludes with a "practice skill challenge" chapter that includes practice problems testing the user on materials just covered. Make sure each course ends with a "final skill challenge" chapter that is an exam of at least 20 unique questions, at least 5 of which are very challenging but still within the bounds of what was taught in the course. 

Please return your results in the following JSON format:
```json
[
    {
        "courseName": "A Course Name",
        "modules": [
            {
                "name": "Module Name",
                "skills": [
                    "A Required Skill",
                    "Another Necessary Skill",
                    "Another Skill, and so on"
                ]
            }
        ]
    }
]
```