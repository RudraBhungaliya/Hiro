import { useState } from 'react'
import DiagramViewer from '../components/DiagramViewer'

function DiagramGenerator() {
  const [path, setPath] = useState('');
  const [diagram, setDiagram] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!path.trim()) {
      setError("Please enter a valid path");
      return;
    }
    setLoading(true);
    setError(null);
    setDiagram(''); // Clear previous diagram

    try {
      // Use absolute URL or proxy if configured. Assuming localhost:8000 for now.
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Analysis failed');
      }

      setDiagram(data.mermaid);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-8 flex flex-col items-center">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600 mb-2">
          Architecture Diagram Generator
        </h1>
        <p className="text-gray-400">AI-Powered Code Structure Visualization</p>
      </header>

      <main className="w-full max-w-5xl space-y-8">
        <div className="bg-gray-900 p-6 rounded-xl border border-gray-800 shadow-lg">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Project Path
          </label>
          <div className="flex gap-4">
            <input
              type="text"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              placeholder="C:\Users\Name\Projects\MyProject"
              className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
            />
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className={`px-8 py-3 rounded-lg font-semibold transition-all flex items-center gap-2
                ${loading
                  ? 'bg-gray-700 cursor-not-allowed text-gray-400'
                  : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/20 shadow-lg'
                }`}
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Scanning...
                </>
              ) : 'Generate Diagram'}
            </button>
          </div>

          <div className="mt-4 flex gap-2">
            <button
              onClick={() => {
                setPath("C:\\Users\\Rudra\\Desktop\\Projects\\Hiro\\server");
              }}
              className="text-xs text-gray-400 hover:text-white underline cursor-pointer"
            >
              👉 Try Demo Path (Hiro Server)
            </button>
          </div>
          {error && (
            <div className="mt-4 p-4 bg-red-900/30 border border-red-800 rounded-lg text-red-200 text-sm flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              {error}
            </div>
          )}
        </div>

        <DiagramViewer chart={diagram} />
      </main>
    </div>
  )
}

export default DiagramGenerator
