from decimal import Decimal, ROUND_HALF_UP


def calculate_completion_cost(model, completion_tokens, prompt_tokens):
    # As of June 5th, 2024
    try:
        model_costs = {
            '3.5': (0.5, 1.5),  # (input, output)
            '4': (5.0, 15.0),
        }

        model_used = model_costs['4']  # default to 4
        model_number = model.split('-')[1]
        for model_key in model_costs.keys():
            if model_number in model_key:
                model_used = model_costs[model_key]

        prompt_cost = Decimal(prompt_tokens / 1000000 * model_used[0])
        completion_cost = Decimal(completion_tokens / 1000000 * model_used[1])
        cost = prompt_cost + completion_cost
        return cost.quantize(Decimal(".01"), rounding=ROUND_HALF_UP)
    except Exception:
        return Decimal('0.00')
