from flask import Flask, request, jsonify
import threading
import json
import main  # Import your scraping script

app = Flask(__name__)

def scrape_yellow_pages(searchterm, location, leadid):
    return main.scrape_yellow_pages(searchterm, location, leadid)

def find_contacts(website_url):
    return main.find_contacts(website_url)

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters"}), 400

    # Synchronously scrape data and return results
    results = scrape_yellow_pages(searchterm, location, leadid)
    return jsonify(results)

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL"}), 400

    # Retrieve contacts for the given website
    contact_results = find_contacts(website_url)
    return jsonify(contact_results)

if __name__ == '__main__':
    app.run(debug=True)
