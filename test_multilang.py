"""
Test Multi-Language Parser
Creates test files if they don't exist, then tests parsing.
"""

from pathlib import Path
from models.multi_language_parser import parse_file_any_language, parse_folder_multi_language
import json


def create_test_files():
    """Create test files for each language."""
    
    # Python test file
    Path('test_python.py').write_text('''
class UserService:
    def __init__(self, database):
        self.db = database
    
    def get_user(self, user_id):
        return self.db.query(user_id)
    
    def create_user(self, name, email):
        return self.db.insert({'name': name, 'email': email})

class DatabaseService:
    def query(self, id):
        pass
    
    def insert(self, data):
        pass
''')
    
    # JavaScript test file
    Path('test_javascript.jsx').write_text('''
import React, { useState, useEffect } from 'react';

function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    
    useEffect(() => {
        fetchUser(userId);
    }, [userId]);
    
    const fetchUser = async (id) => {
        const response = await fetch(`/api/users/${id}`);
        const data = await response.json();
        setUser(data);
    };
    
    return (
        <div className="user-profile">
            <h1>{user?.name}</h1>
        </div>
    );
}

export default UserProfile;
''')
    
    # Java test file
    Path('test_java.java').write_text('''
import org.springframework.web.bind.annotation.*;
import org.springframework.stereotype.Service;

@RestController
@RequestMapping("/api/users")
public class UserController {
    private UserService userService;
    
    @Autowired
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    @GetMapping("/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.findById(id);
    }
    
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.save(user);
    }
}

@Service
public class UserService {
    private UserRepository userRepository;
    
    public User findById(Long id) {
        return userRepository.findById(id);
    }
    
    public User save(User user) {
        return userRepository.save(user);
    }
}
''')
    
    # HTML test file
    Path('test_html.html').write_text('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>User Dashboard</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <nav>
            <a href="/">Home</a>
            <a href="/users">Users</a>
        </nav>
    </header>
    <main>
        <section id="user-list">
            <h1>Users</h1>
        </section>
    </main>
    <script src="app.js"></script>
</body>
</html>
''')
    
    # CSS test file
    Path('test_css.css').write_text('''
.user-profile {
    display: flex;
    flex-direction: column;
    padding: 20px;
}

#user-list {
    margin: 20px 0;
}

@media (max-width: 768px) {
    .user-profile {
        padding: 10px;
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
''')
    
    print("✓ Created test files")


def test_single_files():
    """Test parsing individual files."""
    
    print("\n" + "="*60)
    print("Testing Single File Parsing")
    print("="*60)
    
    test_files = {
        'Python': 'test_python.py',
        'JavaScript': 'test_javascript.jsx',
        'Java': 'test_java.java',
        'HTML': 'test_html.html',
        'CSS': 'test_css.css'
    }
    
    for lang, filepath in test_files.items():
        print(f"\n--- {lang} ---")
        try:
            facts = parse_file_any_language(filepath)
            
            print(f"Language: {facts['language']}")
            print(f"File: {facts['filename']}")
            
            # Handle classes (different structure for different languages)
            if 'classes' in facts and facts['classes']:
                # Check if it's a list of dicts (Python/Java) or strings (CSS)
                if facts['classes'] and isinstance(facts['classes'][0], dict):
                    class_names = [c['name'] for c in facts['classes']]
                    print(f"Classes: {class_names}")
                    
                    # Show methods for first class
                    if facts['classes'][0].get('methods'):
                        print(f"  Methods in {facts['classes'][0]['name']}: {facts['classes'][0]['methods'][:3]}...")
                        
                elif facts['classes'] and isinstance(facts['classes'][0], str):
                    # CSS classes
                    print(f"CSS Classes: {facts['classes'][:5]}...")
            
            # React components
            if 'components' in facts and facts['components']:
                comp_names = [c['name'] for c in facts['components']]
                print(f"Components: {comp_names}")
            
            # React hooks
            if 'hooks' in facts and facts['hooks']:
                print(f"Hooks: {facts['hooks']}")
            
            # React patterns
            if 'react_patterns' in facts and facts['react_patterns']:
                print(f"React Patterns: {facts['react_patterns']}")
            
            # Spring Boot patterns
            if 'spring_patterns' in facts:
                patterns = facts['spring_patterns']
                if any(patterns.values()):  # If any pattern list is not empty
                    print(f"Spring Patterns:")
                    if patterns['controllers']:
                        print(f"  Controllers: {patterns['controllers']}")
                    if patterns['services']:
                        print(f"  Services: {patterns['services']}")
                    if patterns['repositories']:
                        print(f"  Repositories: {patterns['repositories']}")
                    if patterns['entities']:
                        print(f"  Entities: {patterns['entities']}")
            
            # HTML structure
            if 'structure' in facts and facts['structure']:
                print(f"HTML Structure: {facts['structure']}")
            
            # HTML scripts and stylesheets
            if 'scripts' in facts and facts['scripts']:
                print(f"Scripts: {facts['scripts']}")
            if 'stylesheets' in facts and facts['stylesheets']:
                print(f"Stylesheets: {facts['stylesheets']}")
            
            # CSS IDs
            if 'ids' in facts and facts['ids']:
                print(f"CSS IDs: {facts['ids']}")
            
            # CSS animations
            if 'animations' in facts and facts['animations']:
                print(f"Animations: {facts['animations']}")
            
            print("✓ Parsed successfully")
            
        except Exception as e:
            import traceback
            print(f"✗ Error: {e}")
            print("\nFull traceback:")
            traceback.print_exc()


def test_folder():
    """Test parsing entire folder."""
    
    print("\n" + "="*60)
    print("Testing Folder Parsing")
    print("="*60)
    
    # Create a test project folder
    test_project = Path('test_project')
    test_project.mkdir(exist_ok=True)
    
    # Create some files in the test project
    (test_project / 'app.py').write_text('''
class Application:
    def __init__(self):
        self.running = False
    
    def run(self):
        self.running = True
        print("Running app")
    
    def stop(self):
        self.running = False
''')
    
    (test_project / 'App.jsx').write_text('''
import React, { useState } from 'react';

function App() {
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <h1>Hello World</h1>
            <button onClick={() => setCount(count + 1)}>
                Count: {count}
            </button>
        </div>
    );
}

export default App;
''')
    
    try:
        all_facts = parse_folder_multi_language(test_project)
        
        print(f"\n📊 Summary:")
        print(f"Total languages found: {len(all_facts)}")
        
        for lang, facts_list in all_facts.items():
            print(f"\n  {lang.upper()}: {len(facts_list)} file(s)")
            
            for facts in facts_list:
                print(f"    📄 {facts['filename']}")
                
                # Show what was found
                if facts.get('classes') and isinstance(facts['classes'][0], dict):
                    print(f"       Classes: {[c['name'] for c in facts['classes']]}")
                
                if facts.get('components'):
                    print(f"       Components: {[c['name'] for c in facts['components']]}")
                
                if facts.get('hooks'):
                    print(f"       Hooks: {facts['hooks']}")
        
        print("\n✓ Folder parsing successful")
        
    except Exception as e:
        import traceback
        print(f"✗ Error: {e}")
        traceback.print_exc()


def main():
    print("🚀 HIRO Multi-Language Parser Test Suite")
    print("="*60)
    
    # Create test files
    create_test_files()
    
    # Test individual files
    test_single_files()
    
    # Test folder
    test_folder()
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    main()