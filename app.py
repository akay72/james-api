from flask import Flask, request, jsonify
import threading
import main  # Import your scraping script

app = Flask(__name__)

# Dictionary to store ongoing tasks and their results
ongoing_tasks = {}

def scrape_yellow_pages_task(searchterm, location, leadid):
    result = []
    for progress_update in main.scrape_yellow_pages(searchterm, location, leadid):
        result.append(progress_update)
    ongoing_tasks[searchterm] = result

def find_contacts_task(website_url):
    result = []
    for progress_update in main.find_contacts(website_url):
        result.append(progress_update)
    ongoing_tasks[website_url] = result

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters"}), 400

    # Start the scraping task in a separate thread
    scraping_thread = threading.Thread(target=scrape_yellow_pages_task, args=(searchterm, location, leadid))
    scraping_thread.start()

    # Generate a unique task ID (you can use a more robust method in production)
    task_id = scraping_thread.name

    # Return the task ID as a response
    return jsonify({"task_id": task_id, "message": "Scraping task started."}), 202

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL"}), 400

    # Start the contact finding task in a separate thread
    contacts_thread = threading.Thread(target=find_contacts_task, args=(website_url,))
    contacts_thread.start()

    # Generate a unique task ID (you can use a more robust method in production)
    task_id = contacts_thread.name

    # Return the task ID as a response
    return jsonify({"task_id": task_id, "message": "Contact finding task started."}), 202

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    if task_id not in ongoing_tasks:
        return jsonify({"error": "Task not found."}), 404

    task_result = ongoing_tasks.get(task_id)
    if task_result is None:
        return jsonify({"status": "Task in progress..."}), 200
    else:
        return jsonify({"status": "Task completed.", "result": task_result}), 200

if __name__ == '__main__':
    app.run(debug=True)
