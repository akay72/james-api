import openai
import json

def load_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

def generate_outreach_email(config):
    openai.api_key = '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'  # Use your actual API key

    prompt = f"""Lead information: ["{config['lead_name']}","{config['lead_website']}"]
                Product/service details:"National Utilisource is one of the leading North American providers of top-rated energy supply to consumers looking for large-scale energy consumption"""

    messages = [
        {"role": "system", "content": "You are a Sales Representative. Draft an initial outreach email to a potential lead based on the provided details."},
        {"role": "user", "content": prompt}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    return response.choices[0].message['content']

# Load configuration from the JSON file
config_file = r'config.json'
config = load_config(config_file) 
# print(config)

# Generate the outreach email using the loaded configuration
email_content = generate_outreach_email(config)
print(email_content)
