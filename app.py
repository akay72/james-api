from flask import Flask, request, jsonify
import threading
import main  # Import your scraping script
import uuid
from email_content import generate_outreach_email
from flask_cors import CORS
import collections
collections.Iterable = collections.abc.Iterable

app = Flask(__name__)

# CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app, resources={r"/*": {"origins": "*", "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]}})
CORS(app, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
    "methods": ["GET", "POST", "PUT", "DELETE"]
}})
# Dictionary to store ongoing tasks and their results
ongoing_tasks = {}
task_results = {}

def scrape_yellow_pages_task(searchterm, location, leadid, task_id):
    try:
        result = []
        for progress_update in main.scrape_yellow_pages(searchterm, location, leadid):
            result.append(progress_update)
        task_results[task_id] = {'status': 'success', 'result': result}
    except Exception as e:
        task_results[task_id] = {'status': 'error', 'message': str(e)}
    finally:
        print(f"Task {task_id} completed with status {task_results[task_id]['status']}.")
        print(f"Result: {result}")


def find_contacts_task(website_url, task_id):
    try:
        result = []
        for progress_update in main.find_contacts(website_url):
            result.append(progress_update)
        task_results[task_id] = {'status': 'success', 'result': result}
    except Exception as e:
        task_results[task_id] = {'status': 'error', 'message': str(e)}
    finally:
        print(f"Task {task_id} completed with status {task_results[task_id]['status']}.")    
        print(f"Result: {result}")


@app.route('/generate_email', methods=['POST'])
def generate_email():
    data = request.json
    lead_name = data.get('lead_name')
    lead_website = data.get('lead_website')

    if not lead_name or not lead_website:
        return jsonify({"error": "Missing lead_name or lead_website parameters"}), 200

    try:
        # Generate the email content directly without using a separate thread
        email_content = generate_outreach_email(lead_name, lead_website)
        return jsonify({"email_content": email_content, "status": "Task completed."}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred during email generation: {str(e)}"}), 200

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters"}), 200

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Start the scraping task in a separate thread
    scraping_thread = threading.Thread(target=scrape_yellow_pages_task, args=(searchterm, location, leadid, task_id))
    scraping_thread.start()

    # Store the task ID and associated thread in a dictionary
    ongoing_tasks[task_id] = scraping_thread
    print(f"Started scraping task with ID: {task_id}")

    # Return the task ID as a response
    return jsonify({"task_id": task_id, "message": "Scraping task started."}), 200

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL"}), 200

    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Start the contact finding task in a separate thread
    contacts_thread = threading.Thread(target=find_contacts_task, args=(website_url, task_id))
    contacts_thread.start()

    # Store the task ID and associated thread in a dictionary
    ongoing_tasks[task_id] = contacts_thread
    print(f"Started contact finding task with ID: {task_id}")

    # Return the task ID as a response
    return jsonify({"task_id": task_id, "message": "Contact finding task started."}), 200

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    if task_id not in task_results:
        return jsonify({"error": "Task not found."}), 200

    task_info = task_results[task_id]
    if task_info['status'] == 'success':
        return jsonify({"status": "Task completed.", "result": task_info['result']}), 200
    elif task_info['status'] == 'error':
        return jsonify({"status": "Task failed.", "message": task_info['message']}), 200
    else:
        return jsonify({"status": "Task in progress..."}), 200


if __name__ == '__main__':
    app.run(debug=True)
