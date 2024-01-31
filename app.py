from flask import Flask, request, jsonify, Response
import json
import main  # Import your scraping script

app = Flask(__name__)

def scrape_yellow_pages(searchterm, location, leadid):
    # Assuming main.scrape_yellow_pages is a generator that yields progress updates
    return main.scrape_yellow_pages(searchterm, location, leadid)

def find_contacts(website_url):
    # Assuming main.find_contacts is a generator that yields progress updates
    return main.find_contacts(website_url)

@app.route('/company', methods=['POST'])
def company():
    data = request.json
    searchterm = data.get('searchterm')
    location = data.get('location')
    leadid = data.get('leadid')

    if not all([searchterm, location, leadid]):
        return jsonify({"error": "Missing parameters"}), 400

    def generate_scrape_yellow_pages():
        yield "Starting scraping process...\n"
        for progress_update in scrape_yellow_pages(searchterm, location, leadid):
            yield json.dumps(progress_update) + '\n'
        yield "Scraping process completed.\n"

    return Response(generate_scrape_yellow_pages(), mimetype='text/plain')

@app.route('/contacts', methods=['POST'])
def contacts():
    data = request.json
    website_url = data.get('website')

    if not website_url:
        return jsonify({"error": "Missing website URL"}), 400

    def generate_find_contacts():
        yield "Starting contact finding process...\n"
        for progress_update in find_contacts(website_url):
            yield json.dumps(progress_update) + '\n'
        yield "Contact finding process completed.\n"

    return Response(generate_find_contacts(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
