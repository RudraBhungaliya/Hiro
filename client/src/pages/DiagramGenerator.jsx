import { useState } from 'react'
import { Link } from 'react-router-dom'
import DiagramViewer from '../components/DiagramViewer'

function DiagramGenerator() {
  const [path, setPath] = useState('');
  const [diagram, setDiagram] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [diagramCode, setDiagramCode] = useState('');


  const handleAnalyze = async () => {
    if (!path.trim()) {
      setError("Please enter a valid path");
      return;
    }
    setLoading(true);
    setError(null);
    setDiagram('');
    setDiagramCode('');

    try {
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
      setDiagramCode(data.mermaid);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to connect to backend. Make sure the server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(diagramCode);
    // You could add a toast notification here
  };

  const handleDownloadSVG = () => {
    const svg = document.querySelector('.diagram-viewer svg');
    if (svg) {
      const svgData = new XMLSerializer().serializeToString(svg);
      const blob = new Blob([svgData], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'architecture-diagram.svg';
      link.click();
      URL.revokeObjectURL(url);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleAnalyze();
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header with back button */}
      <div className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="text-gray-400 hover:text-white transition-colors flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Home
            </Link>
          </div>
          <div className="text-sm text-gray-400">
            Need help? Check the demo path below
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-8 py-12">
        {/* Hero Section */}
        <header className="mb-12 text-center">
          <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 mb-4">
            Code Architecture & Documentation
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Generate architecture diagrams and comprehensive documentation for your projects
          </p>
        </header>

        {/* Architecture Section */}



        {/* Input Section */}
        <div className="mb-8 bg-gray-900 p-8 rounded-2xl border border-gray-800 shadow-2xl">
          <label className="block text-sm font-semibold text-gray-300 mb-3 uppercase tracking-wide">
            Project Path
          </label>
          <div className="flex gap-4">
            <input
              type="text"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="e.g., C:\Users\Name\Projects\MyProject"
              className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-5 py-4 text-white placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent focus:outline-none transition-all"
            />
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className={`px-10 py-4 rounded-xl font-semibold transition-all flex items-center gap-3 shadow-lg
                ${loading
                  ? 'bg-gray-700 cursor-not-allowed text-gray-400'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white shadow-blue-500/30'
                }`}
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Generate Diagram
                </>
              )}
            </button>
          </div>

          <div className="mt-5 flex flex-wrap gap-3">
            <button
              onClick={() => setPath("C:\\Users\\Rudra\\Desktop\\Projects\\Hiro\\server")}
              className="text-sm px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-gray-300 hover:text-white transition-all flex items-center gap-2"
            >
              <span>📁</span>
              Try Demo Path (Hiro Server)
            </button>
            <div className="flex-1"></div>
            {diagram && (
              <>
                <button
                  onClick={handleCopyCode}
                  className="text-sm px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-gray-300 hover:text-white transition-all flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  Copy Code
                </button>
                <button
                  onClick={handleDownloadSVG}
                  className="text-sm px-4 py-2 bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-500 hover:to-teal-500 rounded-lg text-white transition-all flex items-center gap-2"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download SVG
                </button>
              </>
            )}
          </div>

          {error && (
            <div className="mt-6 p-5 bg-red-900/20 border border-red-800/50 rounded-xl text-red-200 flex items-start gap-3 animate-in fade-in slide-in-from-top-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 flex-shrink-0 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <div>
                <p className="font-semibold mb-1">Analysis Failed</p>
                <p className="text-sm text-red-300">{error}</p>
              </div>
            </div>
          )}
        </div>

        {/* Diagram Display */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-gray-700 border-t-blue-500 rounded-full animate-spin"></div>
              <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-purple-500 rounded-full animate-spin animation-delay-150"></div>
            </div>
            <p className="text-gray-400 text-lg">Analyzing your project structure...</p>
          </div>
        )}

        {!loading && diagram && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-200 flex items-center gap-3">
                <span className="text-3xl">🎨</span>
                Generated Diagram
              </h2>
              <div className="text-sm text-gray-400">
                Use mouse wheel to zoom, drag to pan
              </div>
            </div>
            <DiagramViewer chart={diagram} />
          </div>
        )}

        {!loading && !diagram && !error && (
          <div className="text-center py-20">
            <div className="text-6xl mb-6">📊</div>
            <h3 className="text-2xl font-semibold text-gray-300 mb-3">
              Ready to Visualize Your Code
            </h3>
            <p className="text-gray-500 max-w-md mx-auto">
              Enter your project path above and click "Generate Diagram" to create an interactive architecture visualization
            </p>
          </div>
        )}

      </div>


    </div>
  )
}

export default DiagramGenerator
