from db.db import DB, Response
import math

db = DB()

responses = db.query(Response).filter(
    Response.outline_id == 3,
).all()

costs = {
    'code-editor': [],
    'multiple-choice': [],
    'page-material': [],
}

for response in responses:
    prompt = response.prompt
    total_tokens = response.total_tokens
    cost = total_tokens / 1000000 * 5

    if prompt.subject in costs:
        costs[prompt.subject].append(cost)


def mean(x): return sum(x) / len(x)


print("Interactives Cost:", mean(costs['code-editor']) + mean(costs['multiple-choice']))
print("Page Material Costs:", mean(costs['page-material']))
print("Total Costs Per Page", mean(costs['code-editor']) + mean(costs['multiple-choice']) + mean(costs['page-material']))


# print(f"Response ID: {response.id}, Type: {prompt.subject}, Total Tokens: {total_tokens}, Cost: ${cost}")
