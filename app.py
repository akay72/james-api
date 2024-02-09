from flask import Flask, request, jsonify
import threading
import main  # This should be replaced with the actual import of your scraping functions
import uuid
from threading import Lock

app = Flask(__name__)

# Shared resources
ongoing_tasks = {}
task_results = {}
task_lock = Lock()  # Lock for thread-safe operations on shared resources

def task_wrapper(task_func, *args, **kwargs):
    task_id = kwargs.pop('task_id')
    try:
        # Execute the provided task function
        task_func(*args, **kwargs)
    except Exception as e:
        # In case of an exception, store the error message
        task_results[task_id] = {'error': str(e)}
    finally:
        # Ensure the task is marked as completed in any case
        with task_lock:
            ongoing_tasks.pop(task_id, None)
            if task_id not in task_results:  # Check if not stored by task_func
                task_results[task_id] = {'error': 'Task failed without an error message.'}

def scrape_yellow_pages_task(searchterm, location, leadid, task_id):
    result = []
    # Your scraping logic here
    for progress_update in main.scrape_yellow_pages(searchterm, location, leadid):
        result.append(progress_update)
    task_results[task_id] = result
    print(f"Scraping task {task_id} completed.")

def find_contacts_task(website_url, task_id):
    result = []
    # Your contact finding logic here
    for progress_update in main.find_contacts(website_url):
        result.append(progress_update)
    task_results[task_id] = result
    print(f"Contact finding task for {task_id} completed.")

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters"}), 200

    task_id = str(uuid.uuid4())
    with task_lock:
        ongoing_tasks[task_id] = "processing"
    threading.Thread(target=task_wrapper, args=(scrape_yellow_pages_task,), kwargs={'searchterm': searchterm, 'location': location, 'leadid': leadid, 'task_id': task_id}).start()

    return jsonify({"task_id": task_id, "message": "Scraping task started."}), 200

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL"}), 200

    task_id = str(uuid.uuid4())
    with task_lock:
        ongoing_tasks[task_id] = "processing"
    threading.Thread(target=task_wrapper, args=(find_contacts_task,), kwargs={'website_url': website_url, 'task_id': task_id}).start()

    return jsonify({"task_id": task_id, "message": "Contact finding task started."}), 200

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    with task_lock:
        if task_id in task_results:
            # Remove the result to prevent repeated fetches
            task_result = task_results.pop(task_id)
            return jsonify({"status": "complete", "result": task_result}), 200
        elif task_id in ongoing_tasks:
            return jsonify({"status": "processing"}), 200
        else:
            return jsonify({"error": "Task not found."}), 200

if __name__ == '__main__':
    app.run(debug=True)
