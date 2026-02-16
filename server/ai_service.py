# Mock data response matching the frontend structure
MOCK_ANALYSIS_RESPONSE = {
    "mermaid": """graph TD
    1["Database"]
    2["EmailService"]
    3["AuthService"]
    4["UserService"]
    5["OrderService"]
    6["PaymentService"]
    7("save")
    8("get")
    9("delete")
    10("send_welcome")
    11("send_reset_password")
    12("send_notification")
    13("generate_token")
    14("validate_token")
    15("revoke_token")
    16("register")
    17("login")
    18("delete_account")
    19("reset_password")
    20("place_order")
    21("cancel_order")
    22("get_order")
    23("process_payment")
    24("refund")

    1 -->|has method| 7
    1 -->|has method| 8
    1 -->|has method| 9
    2 -->|has method| 10
    2 -->|has method| 11
    2 -->|has method| 12
    3 -->|has method| 13
    3 -->|has method| 14
    3 -->|has method| 15
    4 -->|has method| 16
    4 -->|has method| 17
    4 -->|has method| 18
    4 -->|has method| 19
    4 -->|depends on| 3
    4 -->|depends on| 1
    4 -->|depends on| 2
    5 -->|has method| 20
    5 -->|has method| 21
    5 -->|has method| 22
    5 -->|depends on| 4
    5 -->|depends on| 1
    5 -->|depends on| 2
    6 -->|has method| 23
    6 -->|has method| 24
    6 -->|depends on| 5
    6 -->|depends on| 1
    6 -->|depends on| 2""",
    "analysis": {
        "fileCount": 7,
        "complexity": "Low",
        "maintainability": "A",
        "languages": ["Python"]
    },
    "insights": [
        { "type": "success", "message": "Architecture Pattern: Service-Oriented Architecture (SOA) detected." },
        { "type": "info", "message": "UserService: Manages user registration, login, account deletion, and password reset." },
        { "type": "info", "message": "OrderService: Handles order-related operations and depends on UserService." },
        { "type": "info", "message": "PaymentService: Processes payments and refunds, loosely coupled with OrderService." },
        { "type": "info", "message": "AuthService: Standalone service for token generation and validation." },
        { "type": "info", "message": "EmailService: Handles all communication, no external dependencies." },
        { "type": "info", "message": "Database: Central data store with basic CRUD operations." }
    ]
}

def analyze_codebase(files):
    """
    This function should interface with the AI model.
    Input: list of file dicts {name, path, content, type}
    Output: JSON structure with mermaid code and analysis insights.
    """
    
    # TODO: Integrate with actual AI model here.
    # Code would look something like:
    # prompt = create_prompt(files)
    # response = ai_client.chat.completions.create(...)
    # return parse_response(response)
    
    print(f"Received {len(files)} files for analysis.")
    
    # For now, return mock data
    # We can perform some simple analysis on the 'files' to make it slightly dynamic if we wanted,
    # but for MVP, fixed mock data is safer to ensure frontend renders correctly first.
    
    response = MOCK_ANALYSIS_RESPONSE.copy()
    response["analysis"]["fileCount"] = len(files)
    
    # Simple language detection based on files
    languages = set()
    for f in files:
        if f['type'] == 'js' or f['type'] == 'jsx':
            languages.add("JavaScript")
        elif f['type'] == 'py':
            languages.add("Python")
        elif f['type'] == 'html':
            languages.add("HTML")
        elif f['type'] == 'css':
            languages.add("CSS")
            
    response["analysis"]["languages"] = list(languages)
    
    return response
