Using the provided list of required skills for mastery of {topic}, please create an outline for a series of as many small courses as you think are needed that can ideally be consumed in less than two hours. Each course should have at least two modules. Reorganize the items as needed, and try to make each course relatively independent. Make sure each chapter concludes with a "practice skill challenge" chapter that includes practice problems testing the user on materials just covered.

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