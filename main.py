import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, render_template_string, jsonify

# Flask app for the HTML interface
app = Flask(__name__)

def fetch_trending_topics():
    # Set up Selenium without proxy
    options = Options()
    driver = webdriver.Chrome(options=options)

    try:
        # Log in to Twitter (manual login if session reuse not implemented)
        driver.get("https://x.com/i/flow/login")
        
        # Wait for login process if needed (manually log in)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'r-18u37iz')]/span"))
        )

        # Scrape the trending topics (using the correct XPath to locate the topic span elements)
        # Find div elements with class 'css-146c3p1' which is common to all trending topic divs
        trending_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'css-146c3p1')]/span[contains(@class, 'css-1jxf684') or contains(@class, 'r-poiln3')]")

        # Extract the text of each trending topic
        trending_topics = [el.text for el in trending_elements if el.text.strip()]

        # Limit to top 5 trends
        trending_topics = trending_topics[:5]  # Only take the top 5 topics

        # Create a dictionary for trending topics
        record = {
            "trend1": trending_topics[0] if len(trending_topics) > 0 else None,
            "trend2": trending_topics[1] if len(trending_topics) > 1 else None,
            "trend3": trending_topics[2] if len(trending_topics) > 2 else None,
            "trend4": trending_topics[3] if len(trending_topics) > 3 else None,
            "trend5": trending_topics[4] if len(trending_topics) > 4 else None,
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Write to an HTML file in the root directory
        with open("trending_topics.html", "w") as file:
            file.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Trending Topics</title>
            </head>
            <body>
                <h1>Trending Topics</h1>
                <ul>
                    <li>{record['trend1']}</li>
                    <li>{record['trend2']}</li>
                    <li>{record['trend3']}</li>
                    <li>{record['trend4']}</li>
                    <li>{record['trend5']}</li>
                </ul>
                <p>Fetched at: {record['datetime']}</p>
            </body>
            </html>
            """)

        return record

    finally:
        driver.quit()


@app.route('/')
def home():
    html_template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Twitter Trending Topics</title>
    </head>
    <body>
        <h1>Twitter Trending Topics</h1>
        <button onclick="runScript()">Click here to run the script</button>
        <pre id="output"></pre>
        <script>
            async function runScript() {
                const response = await fetch('/run-script');
                const data = await response.json();
                document.getElementById('output').innerText = JSON.stringify(data, null, 2);
                alert('Trending topics saved to trending_topics.html!');
            }
        </script>
    </body>
    </html>
    '''
    return html_template


@app.route('/run-script', methods=['GET'])
def run_script():
    # Fetch the trending topics and return as JSON response
    record = fetch_trending_topics()
    return jsonify(record)


if __name__ == '__main__':
    app.run(debug=True)
