from flask import Flask, request, jsonify
import threading
import main  # Import your scraping and contact finding module
import uuid

app = Flask(__name__)

# Dictionaries to store ongoing tasks and their results
ongoing_tasks = {}
task_results = {}

def scrape_yellow_pages_task(searchterm, location, leadid, task_id):
    try:
        result = []
        for progress_update in main.scrape_yellow_pages(searchterm, location, leadid):
            result.append(progress_update)
        if not result:
            task_results[task_id] = {"status": "success", "result": "No results found on Yellow Pages."}
        else:
            task_results[task_id] = {"status": "success", "result": result}
    except Exception as e:
        task_results[task_id] = {"status": "failed", "error": str(e)}
    finally:
        print(f"Scraping task {task_id} completed.")
        print(f"Result: {task_results[task_id]}")

def find_contacts_task(website_url, task_id):
    try:
        result = []
        for progress_update in main.find_contacts(website_url):
            result.append(progress_update)
        if not result:
            task_results[task_id] = {"status": "success", "result": "No contact information found."}
        else:
            task_results[task_id] = {"status": "success", "result": result}
    except Exception as e:
        task_results[task_id] = {"status": "failed", "error": str(e)}
    finally:
        print(f"Contact finding task for {task_id} completed.")
        print(f"Result: {task_results[task_id]}")

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters", "success": False}), 200

    task_id = str(uuid.uuid4())
    scraping_thread = threading.Thread(target=scrape_yellow_pages_task, args=(searchterm, location, leadid, task_id))
    scraping_thread.start()
    ongoing_tasks[task_id] = scraping_thread
    return jsonify({"task_id": task_id, "message": "Scraping task started.", "success": True}), 200

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL", "success": False}), 200

    task_id = str(uuid.uuid4())
    contacts_thread = threading.Thread(target=find_contacts_task, args=(website_url, task_id))
    contacts_thread.start()
    ongoing_tasks[task_id] = contacts_thread
    return jsonify({"task_id": task_id, "message": "Contact finding task started.", "success": True}), 200

@app.route('/task_status/<task_id>', methods=['GET'])
def task_status(task_id):
    if task_id not in task_results:
        return jsonify({"error": "Task not found.", "success": False}), 200

    task_result = task_results[task_id]
    if task_result['status'] == "success":
        return jsonify({"status": "Task completed successfully.", "result": task_result['result'], "success": True}), 200
    elif task_result['status'] == "failed":
        return jsonify({"status": "Task failed.", "error": task_result['error'], "success": False}), 200

if __name__ == '__main__':
    app.run(debug=True)
