import requests
import os

# Use the current server directory as the test path
TEST_PATH = os.path.dirname(os.path.abspath(__file__))

def test_analyze_api():
    url = "http://localhost:8000/api/analyze"
    payload = {"path": TEST_PATH}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        print("Status Code:", response.status_code)
        print("Keys received:", list(data.keys()))
        
        if "mermaid" in data and "analysis" in data and "insights" in data:
            print("SUCCESS: Response contains all required fields.")
            print("Mermaid length:", len(data["mermaid"]))
            print("File count:", data["analysis"].get("fileCount"))
        else:
            print("FAILURE: Missing fields in response.")
            print("Response:", data)
            
    except requests.exceptions.JSONDecodeError:
        print("ERROR: Failed to decode JSON.")
        print("Raw Response:", response.text)
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Is it running?")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_analyze_api()
