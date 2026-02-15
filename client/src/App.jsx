import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import DiagramGenerator from './pages/DiagramGenerator'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/diagram-generator" element={<DiagramGenerator />} />
      </Routes>
    </Router>
  )
}

function HomePage() {
  const services = [
    {
      id: 1,
      title: "Architecture Diagram Generator",
      description: "Generate beautiful architecture diagrams from your codebase using AI",
      icon: "📊",
      route: "/diagram-generator",
      color: "from-blue-500 to-purple-600",
      available: true
    },
    {
      id: 2,
      title: "Code Documentation",
      description: "Automatically generate comprehensive documentation for your projects",
      icon: "📚",
      route: "/documentation",
      color: "from-green-500 to-teal-600",
      available: false
    },
    {
      id: 3,
      title: "API Analyzer",
      description: "Analyze and visualize your API endpoints and dependencies",
      icon: "🔌",
      route: "/api-analyzer",
      color: "from-orange-500 to-red-600",
      available: false
    },
    {
      id: 4,
      title: "Code Quality Insights",
      description: "Get AI-powered insights on code quality and improvements",
      icon: "⚡",
      route: "/code-insights",
      color: "from-purple-500 to-pink-600",
      available: false
    }
  ];

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10"></div>
        <div className="relative max-w-7xl mx-auto px-8 py-20">
          <div className="text-center">
            <h1 className="text-6xl font-bold mb-6">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500">
                Hiro
              </span>
            </h1>
            <p className="text-2xl text-gray-300 mb-4">
              AI-Powered Development Tools
            </p>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Enhance your development workflow with intelligent code analysis, visualization, and documentation tools
            </p>
          </div>
        </div>
      </div>

      {/* Services Grid */}
      <div className="max-w-7xl mx-auto px-8 py-16">
        <h2 className="text-3xl font-bold mb-12 text-center">Our Services</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-8">
          {services.map((service) => (
            <ServiceCard key={service.id} service={service} />
          ))}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-20">
        <div className="max-w-7xl mx-auto px-8 py-8 text-center text-gray-400">
          <p>© 2026 Hiro. AI-Powered Development Tools.</p>
        </div>
      </footer>
    </div>
  );
}

function ServiceCard({ service }) {
  const CardContent = () => (
    <div className={`relative h-full bg-gray-900 rounded-xl border border-gray-800 p-8 transition-all duration-300 hover:border-gray-700 hover:shadow-2xl group ${!service.available ? 'opacity-60' : ''}`}>
      <div className={`absolute inset-0 bg-gradient-to-br ${service.color} opacity-0 group-hover:opacity-10 rounded-xl transition-opacity duration-300`}></div>
      
      <div className="relative z-10">
        <div className="text-5xl mb-4">{service.icon}</div>
        <h3 className="text-2xl font-bold mb-3 flex items-center gap-2">
          {service.title}
          {!service.available && (
            <span className="text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded-full">Coming Soon</span>
          )}
        </h3>
        <p className="text-gray-400 mb-6">{service.description}</p>
        
        <div className={`inline-flex items-center gap-2 text-sm font-semibold ${service.available ? 'text-blue-400' : 'text-gray-500'}`}>
          {service.available ? (
            <>
              Launch Service
              <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </>
          ) : (
            'In Development'
          )}
        </div>
      </div>
    </div>
  );

  if (service.available) {
    return (
      <Link to={service.route} className="block h-full">
        <CardContent />
      </Link>
    );
  }

  return (
    <div className="cursor-not-allowed">
      <CardContent />
    </div>
  );
}

export default App
