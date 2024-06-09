from decimal import Decimal
from src.utils.llm.calculate_completion_cost import calculate_completion_cost


def test_calculate_4_model_costs():
    model = 'gpt-4o-2024-05-13'
    completion_tokens = 1119
    prompt_tokens = 32149
    costs = calculate_completion_cost(model, completion_tokens, prompt_tokens)
    assert costs == Decimal('0.18')


def test_calculate_3_5_model_costs():
    model = 'gpt-3.5-turbo-0125'
    completion_tokens = 76
    prompt_tokens = 899
    costs = calculate_completion_cost(model, completion_tokens, prompt_tokens)
    assert costs == Decimal('0.00')  # Honestly not sure how they're calculating such small costs on their side.
