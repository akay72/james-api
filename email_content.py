import openai
import os
# Load configuration from the JSON file
# def generate_outreach_email(lead_name, lead_website):
#     # Set your OpenAI API key here. Consider using environment variables for production
#     openai.api_key = os.getenv('OPENAI_API_KEY')
    
#     prompt = f"""Lead information: ["{lead_name}","{lead_website}"]
#                 Product/service details: "National Utilisource is one of the leading North American providers of top-rated energy supply to consumers looking for large-scale energy consumption."""
#     messages = [
#         {"role": "system", "content": "You are a Sales Representative. Draft an initial outreach email to a potential lead based on the provided details."},
#         {"role": "user", "content": prompt}
#     ]

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=messages
#     )

#     return response.choices[0].message['content']

def generate_outreach_email(lead_name, lead_website):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    prompt = f"""Lead information: ["{lead_name}","{lead_website}"]
Product/service details: "National Utilisource is one of the leading North American providers of top-rated energy supply to consumers looking for large-scale energy consumption. Based on this information, create an email with the subject clearly labeled as 'Subject:' and the body of the email labeled as 'Body:'. The email should be tailored to the lead, highlighting the benefits of National Utilisource's services."""

    try:
        completion = client.chat.completions.create(
            model="gpt-4",  # Adjust according to the model you're intending to use
            messages=[
                {"role": "system", "content": "You are a Sales Representative. Draft an initial outreach email to a potential lead based on the provided details."},
                {"role": "user", "content": prompt}
            ]
        )

        # Assuming the output is structured with 'Subject:' and 'Body:' as markers
        output = completion.choices[0].message.content
        subject_start_index = output.find('Subject:') + len('Subject:')
        body_start_index = output.find('Body:', subject_start_index) + len('Body:')

        subject = output[subject_start_index:body_start_index - len('Body:')].strip()
        body = output[body_start_index:].strip()

        return {"subject": subject, "body": body}
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
