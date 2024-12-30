import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, jsonify

# Flask app for the HTML interface
app = Flask(__name__)

def fetch_trending_topics():
    # Set up Selenium options
    options = Options()
    driver = webdriver.Chrome(options=options)

    try:
        # Step 1: Navigate to the login page
        driver.get("https://x.com/i/flow/login")
        
        # Step 2: Wait for redirection to the homepage after manual login
        print("Please log in manually...")
        WebDriverWait(driver, 300).until(
            lambda d: d.current_url == "https://x.com/home"
        )
        print("Login successful, redirected to homepage!")

        # Step 3: Redirect to the explore page
        driver.get("https://x.com/explore/tabs/for-you")
        
        # Step 4: Wait for the relevant data to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='cellInnerDiv']//div//div//div[@role='link']//div//div[@dir='ltr']//span[@dir='ltr']"))
        )
        # Step 5: Scrape data from the required hierarchy
        elements = driver.find_elements(By.XPATH, "//div[@data-testid='cellInnerDiv']//div//div//div[@role='link']//div//div[@dir='ltr']//span[@dir='ltr']")
        data = [el.text for el in elements if el.text.strip()]

        # Step 6: Create a record for the data
        record = {
            "trending_data": data[:5],  # Fetch top 5 results
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Save to an HTML file
        with open("trending_topics.html", "w") as file:
            file.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Trending Topics</title>
            </head>
            <body>
                <h1>Trending Topicss</h1>
                <ul>
                    {''.join(f'<li>{topic}</li>' for topic in record['trending_data'])}
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
    # Fetch trending topics and return as JSON response
    record = fetch_trending_topics()
    return jsonify(record)


if __name__ == '__main__':
    app.run(debug=True)
