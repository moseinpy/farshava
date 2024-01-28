# openai_client.py
import openai
from django.conf import settings


def initialize_openai():
    openai.api_key = settings.OPENAI_API_KEY


def generate_code(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500
    )
    generated_code = response['choices'][0]['text']

    # چاپ کد تولید شده
    print("Generated Code:")
    print(generated_code)

    return generated_code


def generate_rain_gauge_model(station_name, location, elevation, annual_rainfall):
    prompt = f"""
    Create a rain gauge station model for the station "{station_name}".
    The station is located at {location}, has an elevation of {elevation} meters,
    and receives an annual rainfall of {annual_rainfall} millimeters.
    Provide recommendations for managing the rain gauge data and any actions to be taken based on this information.
    """

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=500
    )

    generated_model = response['choices'][0]['text']

    # چاپ مدل تولید شده
    print("Generated Rain Gauge Model:")
    print(generated_model)

    return generated_model
