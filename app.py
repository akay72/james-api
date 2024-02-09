from flask import Flask, request, jsonify
import threading
import main  # Assuming main.py contains your scraping functions
import uuid

app = Flask(__name__)

# Dictionary to store ongoing tasks and their results
ongoing_tasks = {}
task_results = {}

def scrape_yellow_pages_task(searchterm, location, leadid, task_id):
    result = []
    # Simulate scraping task with updates
    for progress_update in main.scrape_yellow_pages(searchterm, location, leadid):
        result.append(progress_update)
    task_results[task_id] = result
    # Once completed, remove from ongoing tasks
    ongoing_tasks.pop(task_id, None)
    print(f"Scraping task {task_id} completed.")
    print(f"Result: {result}")

def find_contacts_task(website_url, task_id):
    result = []
    # Simulate contact finding task with updates
    for progress_update in main.find_contacts(website_url):
        result.append(progress_update)
    task_results[task_id] = result
    # Once completed, remove from ongoing tasks
    ongoing_tasks.pop(task_id, None)
    print(f"Contact finding task for {task_id} completed.")
    print(f"Result: {result}")

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters"}), 200

    task_id = str(uuid.uuid4())
    scraping_thread = threading.Thread(target=scrape_yellow_pages_task, args=(searchterm, location, leadid, task_id))
    scraping_thread.start()
    ongoing_tasks[task_id] = "processing"
    print(f"Started scraping task with ID: {task_id}")

    return jsonify({"task_id": task_id, "message": "Scraping task started."}), 200

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL"}), 200

    task_id = str(uuid.uuid4())
    contacts_thread = threading.Thread(target=find_contacts_task, args=(website_url, task_id))
    contacts_thread.start()
    ongoing_tasks[task_id] = "processing"
    print(f"Started contact finding task with ID: {task_id}")

    return jsonify({"task_id": task_id, "message": "Contact finding task started."}), 200

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    if task_id in task_results:
        task_result = task_results[task_id]
        return jsonify({"status": "complete", "result": task_result}), 200
    elif task_id in ongoing_tasks:
        return jsonify({"status": "processing"}), 200
    else:
        return jsonify({"error": "Task not found."}), 200

if __name__ == '__main__':
    app.run(debug=True)
