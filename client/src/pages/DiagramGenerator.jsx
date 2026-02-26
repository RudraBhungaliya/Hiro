import { useState } from 'react'
import { Link } from 'react-router-dom'
import DiagramViewer from '../components/DiagramViewer'
import AnalysisPanel from '../components/AnalysisPanel'
import { generateArchitectureReport } from '../utils/reportGenerator'

function DiagramGenerator() {
  const [path, setPath] = useState('');
  const [diagram, setDiagram] = useState('');
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [diagramCode, setDiagramCode] = useState('');
  const [activeTab, setActiveTab] = useState('diagram');

  const handleAnalyze = async () => {
    if (!path.trim()) {
      setError("Please enter a valid path");
      return;
    }
    setLoading(true);
    setError(null);
    setDiagram('');
    setDiagramCode('');
    setAnalysisData(null);

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          path: path.trim(),
          mode: "auto"
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to analyze project");
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error("Analysis failed");
      }

      setDiagram(data.mermaid);
      setDiagramCode(data.mermaid);
      setAnalysisData(data.description);
      setActiveTab('diagram');

    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to analyze project.");
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(diagramCode);
    // You could add a toast notification here
  };

  const handleDownloadReport = () => {
    // analysisData is the documentation string
    generateArchitectureReport(diagramCode, analysisData);
  };

  const handleDownloadSVG = () => {
    const svg = document.querySelector('.mermaid-diagram svg');
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
    <div className="min-h-screen bg-[#f9f5ee] text-slate-900">
      <div className="border-b border-slate-300/70 bg-[#f7efe2]/90 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 sm:px-10 py-3 flex items-center justify-between gap-4">
          <Link
            to="/"
            className="text-xs sm:text-sm text-slate-600 hover:text-slate-900 transition-colors inline-flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to home
          </Link>
          <div className="hidden sm:block text-xs text-slate-500">
            Paste a local folder path or a GitHub URL.
          </div>
        </div>
      </div>

      <div className="w-full h-full px-4 sm:px-6 lg:px-10 py-8">
        <header className="max-w-6xl mx-auto mb-10 flex flex-col gap-2">
          <p className="text-[11px] tracking-[0.25em] font-semibold text-orange-600 uppercase">
            Code architecture generator
          </p>
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-semibold text-slate-900">
            From Python files to a clean diagram.
          </h1>
          <p className="text-sm sm:text-base text-slate-700 max-w-2xl">
            Describe the project by its path, hit generate, and Hiro sketches the structure for you
            — like a whiteboard explanation that stays in sync with the code.
          </p>
        </header>

        <div className="max-w-6xl mx-auto mb-8 rounded-3xl border border-slate-300 bg-[#fdf8f0] px-5 sm:px-7 py-6 shadow-[0_16px_38px_rgba(15,23,42,0.08)]">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-slate-700 mb-2 uppercase tracking-[0.18em]">
                Project path or GitHub URL
              </label>
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="text"
                  value={path}
                  onChange={(e) => setPath(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="/Users/you/project  ·  https://github.com/user/repo"
                  className="flex-1 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 placeholder-slate-400 shadow-sm focus:outline-none focus:ring-2 focus:ring-orange-400/70 focus:border-orange-400"
                />
                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className={`min-w-[160px] rounded-xl px-5 py-3 text-sm font-semibold inline-flex items-center justify-center gap-2 shadow-md shadow-orange-300/60 transition-colors ${
                    loading
                      ? 'bg-slate-300 cursor-wait text-slate-600'
                      : 'bg-orange-500 hover:bg-orange-600 text-[#fdf8f0]'
                  }`}
                >
                  {loading ? (
                    <>
                      <svg
                        className="animate-spin h-4 w-4"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Generating…
                    </>
                  ) : (
                    <>
                      <span className="text-base">🧮</span>
                      Generate diagram
                    </>
                  )}
                </button>
              </div>

              <div className="mt-3 flex flex-wrap items-center gap-3 text-[11px] text-slate-600">
                <button
                  onClick={() => setPath("https://github.com/fastapi/fastapi")}
                  className="inline-flex items-center gap-2 rounded-full border border-dashed border-slate-400/70 bg-white px-3 py-1.5 text-[11px] hover:border-orange-500 hover:text-orange-700 transition-colors"
                >
                  <span>📁</span>
                  Use sample: fastapi/fastapi
                </button>
                {diagram && (
                  <>
                    <button
                      onClick={handleCopyCode}
                      className="inline-flex items-center gap-1.5 rounded-full border border-slate-400/70 bg-white px-3 py-1.5 text-[11px] hover:border-slate-700 hover:text-slate-800 transition-colors"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                        />
                      </svg>
                      Copy Mermaid
                    </button>
                    <button
                      onClick={handleDownloadSVG}
                      className="inline-flex items-center gap-1.5 rounded-full border border-slate-400/70 bg-white px-3 py-1.5 text-[11px] hover:border-slate-700 hover:text-slate-800 transition-colors"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                        />
                      </svg>
                      Export SVG
                    </button>
                    <button
                      onClick={handleDownloadReport}
                      className="inline-flex items-center gap-1.5 rounded-full border border-slate-400/70 bg-white px-3 py-1.5 text-[11px] hover:border-slate-700 hover:text-slate-800 transition-colors"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                      Download report
                    </button>
                  </>
                )}
              </div>

              {error && (
                <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-xs flex gap-3 text-red-800">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4 flex-shrink-0 mt-0.5"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <div>
                    <p className="font-semibold mb-0.5">Analysis failed</p>
                    <p>{error}</p>
                    {error.includes("Failed to fetch") && (
                      <p className="mt-1 text-[11px] text-red-700/80">
                        Ensure the backend server is running on port 8000 before generating a diagram.
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>

            <div className="hidden md:block w-px bg-slate-300/80 mx-2" />
            <div className="md:w-56 text-[11px] text-slate-600 space-y-2 md:pl-2">
              <p className="font-semibold text-slate-700">Hint board</p>
              <p>Best results with Python services and libraries.</p>
              <p>Virtual environments and caches are skipped automatically.</p>
              <p>Use the tabs below to switch between diagram and written documentation.</p>
            </div>
          </div>
        </div>

        <div className="max-w-6xl mx-auto">
          {loading && (
            <div className="flex flex-col items-center justify-center py-16 gap-3 text-slate-700">
              <div className="relative">
                <div className="w-12 h-12 border-4 border-slate-300 border-t-orange-500 rounded-full animate-spin"></div>
              </div>
              <p className="text-sm sm:text-base">Analyzing your project structure…</p>
              <p className="text-[11px] text-slate-500">
                This may take a moment for larger repositories.
              </p>
            </div>
          )}

          {!loading && diagram && (
            <div className="space-y-5">
              <div className="flex gap-2 border-b border-slate-300 mb-4 text-xs sm:text-sm">
                <button
                  onClick={() => setActiveTab('diagram')}
                  className={`px-4 py-2 font-medium transition-colors border-b-2 ${
                    activeTab === 'diagram'
                      ? 'border-orange-500 text-slate-900'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Diagram
                </button>
                <button
                  onClick={() => setActiveTab('analysis')}
                  className={`px-4 py-2 font-medium transition-colors border-b-2 ${
                    activeTab === 'analysis'
                      ? 'border-orange-500 text-slate-900'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  Documentation
                </button>
              </div>

              {activeTab === 'diagram' && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="flex items-center justify-between mb-3">
                    <h2 className="text-lg sm:text-xl font-semibold text-slate-900 flex items-center gap-2">
                      <span className="text-2xl">🎨</span>
                      Generated diagram
                    </h2>
                    <div className="text-[11px] text-slate-500">
                      Scroll to zoom, drag to pan inside the board.
                    </div>
                  </div>
                  <DiagramViewer chart={diagram} />
                </div>
              )}

              {activeTab === 'analysis' && (
                <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <AnalysisPanel data={analysisData} />
                </div>
              )}
            </div>
          )}

          {!loading && !diagram && !error && (
            <div className="text-center py-16">
              <div className="text-5xl mb-4">📋</div>
              <h3 className="text-xl font-semibold text-slate-900 mb-2">
                Ready to sketch your architecture.
              </h3>
              <p className="text-sm text-slate-600 max-w-md mx-auto">
                Enter a path or repository above, then generate to see your project drawn out like a
                whiteboard diagram.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DiagramGenerator
