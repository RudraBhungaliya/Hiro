import { Link } from 'react-router-dom'

export default function Home() {
  const services = [
    {
      id: 1,
      title: "Code Architecture & Documentation",
      description: "Generate architecture diagrams and comprehensive documentation for your projects",
      icon: "📊 📚",
      route: "/diagram-generator",
      color: "from-blue-500 via-purple-500 to-pink-500",
      available: true
    },
    {
      id: 2,
      title: "Code Quality Insights",
      description: "Get AI-powered insights on code quality and improvements",
      icon: "⚡",
      route: "#",
      color: "from-orange-500 to-red-500",
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
      <div className="max-w-7xl mx-auto px-8 py-16 flex justify-center">
        <div className="w-full max-w-6xl">
          <h2 className="text-3xl font-bold mb-12 text-center">Our Services</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {services.map((service) => (
              <ServiceCard key={service.id} service={service} />
            ))}
          </div>
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
  const handleMouseMove = (e) => {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();

    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * -10;
    const rotateY = ((x - centerX) / centerX) * 10;

    card.style.transform = `
      rotateX(${rotateX}deg)
      rotateY(${rotateY}deg)
      scale(1.03)
    `;

    // Update glare effect
    const glare = card.querySelector('.glare-effect');
    if (glare) {
      glare.style.background = `radial-gradient(circle at ${x}px ${y}px, rgba(255, 255, 255, 0.15), transparent 50%)`;
    }
  };

  const handleMouseLeave = (e) => {
    e.currentTarget.style.transform = `
      rotateX(0deg)
      rotateY(0deg)
      scale(1)
    `;
  };

  const CardContent = () => (
    <div
      className={`relative h-full bg-gray-900 rounded-xl border border-gray-800 p-8 hover:border-gray-700 hover:shadow-2xl group ${!service.available ? 'opacity-60' : ''}`}
      style={{
        transformStyle: 'preserve-3d',
        transition: 'all 0.1s ease-out',
      }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${service.color} opacity-0 group-hover:opacity-10 rounded-xl transition-opacity duration-300`}></div>

      <div className="relative z-10 flex flex-col items-center text-center">
        <div className="text-6xl mb-6 transition-transform duration-300 group-hover:scale-110">{service.icon}</div>
        <h3 className="text-3xl font-bold mb-4 flex items-center justify-center gap-3">
          {service.title}
          {!service.available && (
            <span className="text-xs bg-gray-800 text-gray-400 px-2 py-1 rounded-full">Coming Soon</span>
          )}
        </h3>
        <p className="text-xl text-gray-400 mb-8 max-w-lg">{service.description}</p>

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

      {/* Glare effect */}
      <div
        className="glare-effect absolute inset-0 rounded-xl pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{
          background: 'radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.15), transparent 50%)',
        }}
      />
    </div>
  );

  if (service.available) {
    return (
      <div className="h-full" style={{ perspective: '1000px' }}>
        <Link to={service.route} className="block h-full">
          <CardContent />
        </Link>
      </div>
    );
  }

  return (
    <div className="h-full cursor-not-allowed" style={{ perspective: '1000px' }}>
      <CardContent />
    </div>
  );
}

