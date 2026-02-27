import { Link } from 'react-router-dom';
import AuthBtn from '../components/AuthBtn';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#f9f5ee] text-slate-900">
      {/* Hero / Whiteboard section */}
      <section className="relative overflow-hidden border-b border-orange-100/60 bg-gradient-to-b from-[#fbf7ef] to-[#f4ebdd]">
        <div className="absolute inset-y-0 left-0 w-1 bg-slate-800/50 translate-x-10 sm:translate-x-20" />
        
        {/* Auth Button in top right */}
        <div className="absolute top-6 right-6 z-10">
          <AuthBtn />
        </div>

        <div className="max-w-6xl mx-auto px-6 sm:px-10 py-16 sm:py-20 lg:py-24 flex flex-col lg:flex-row gap-14 items-center">
          {/* Left: pixel logo + copy */}
          <div className="flex-1 space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-xs font-semibold tracking-wide text-orange-700">
              CODE ARCHITECTURE DIAGRAMS
            </div>

            <div className="leading-none tracking-[0.25em] font-black text-[40px] sm:text-[52px] md:text-[64px] text-orange-500 drop-shadow-[0_0_0_rgba(0,0,0,0)] pixel-hiro">
              HIRO
            </div>

            <p className="text-lg sm:text-xl text-slate-800 max-w-xl">
              Turn real codebases into clean architecture diagrams and plain‑English documentation.
              No manual drawing, no stale docs — just up‑to‑date structure on a glance.
            </p>

            <p className="text-sm sm:text-base text-slate-600 max-w-xl">
              Paste a local path or GitHub URL, and Hiro will analyze classes, functions, and
              dependencies to build a diagram you can explore, export, and share with your team.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link
                to="/diagram-generator"
                className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-[#f9f5ee] shadow-md shadow-slate-400/40 hover:bg-slate-800 transition-colors"
              >
                Start Generating Diagrams
                <span className="text-base">↗</span>
              </Link>
              <span className="text-xs sm:text-sm text-slate-500">
                Works with Python folders and public GitHub repositories.
              </span>
            </div>
          </div>

          {/* Right: stacked “screens” that look like diagrams */}
          <div className="flex-1 w-full flex justify-center">
            <div className="relative w-full max-w-md">
              <div className="absolute -top-6 -left-6 w-20 h-20 rounded-full bg-orange-200/60 blur-2xl" />
              <div className="absolute -bottom-8 -right-10 w-24 h-24 rounded-full bg-slate-300/50 blur-3xl" />

              <div className="relative space-y-5">
                {/* Top card: code → diagram */}
                <div className="rounded-2xl bg-white shadow-[0_18px_45px_rgba(15,23,42,0.15)] border border-slate-200 overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-2 border-b border-slate-200 bg-slate-50">
                    <span className="text-xs font-semibold tracking-wide text-slate-600">
                      PYTHON PROJECT
                    </span>
                    <span className="text-[10px] text-slate-400">analyzing…</span>
                  </div>
                  <div className="flex gap-4 px-4 py-4">
                    <div className="flex-1 space-y-1 text-xs font-mono text-slate-700">
                      <p>BinarySearchService</p>
                      <p>GraphBuilder</p>
                      <p>FolderParser</p>
                      <p className="text-slate-400">…and more</p>
                    </div>
                    <div className="flex-1 rounded-xl border border-slate-200 bg-slate-50/80 px-3 py-2 text-[10px] text-slate-700">
                      <p className="font-semibold mb-1">Overview</p>
                      <p>Classes organized into layers with clear dependencies and call flow.</p>
                    </div>
                  </div>
                </div>

                {/* Bottom card: simplified diagram */}
                <div className="rounded-2xl bg-white shadow-[0_16px_38px_rgba(15,23,42,0.14)] border border-slate-200 px-4 py-4">
                  <div className="mb-3 flex items-center justify-between">
                    <span className="text-xs font-semibold tracking-wide text-slate-600">
                      GENERATED ARCHITECTURE
                    </span>
                    <span className="text-[10px] text-slate-400">zoom • pan • export</span>
                  </div>

                  <div className="relative h-40 sm:h-44">
                    <div className="absolute inset-0 rounded-xl border border-slate-200 bg-[radial-gradient(circle_at_1px_1px,#e5e7eb_1px,transparent_0)] bg-[length:18px_18px]" />
                    <div className="relative h-full flex items-center justify-center">
                      <div className="flex flex-col items-center gap-2">
                        <div className="flex gap-4">
                          <span className="rounded-md border border-slate-400 bg-white px-2 py-1 text-[11px]">
                            Parser
                          </span>
                          <span className="rounded-md border border-slate-400 bg-white px-2 py-1 text-[11px]">
                            GraphBuilder
                          </span>
                          <span className="rounded-md border border-slate-400 bg-white px-2 py-1 text-[11px]">
                            Renderer
                          </span>
                        </div>
                        <span className="h-6 w-px bg-slate-500" />
                        <span className="rounded-md border border-slate-500 bg-slate-900 px-3 py-1 text-[11px] font-semibold text-orange-50">
                          Mermaid Diagram
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Scrolling content sections */}
      <main className="max-w-6xl mx-auto px-6 sm:px-10 py-12 space-y-20">
        {/* About paragraph */}
        <section className="grid md:grid-cols-[1.3fr_minmax(0,1fr)] gap-10 items-start">
          <div>
            <h2 className="text-2xl sm:text-3xl font-semibold text-slate-900 mb-4">
              Understand your codebase like a whiteboard lesson.
            </h2>
            <p className="text-sm sm:text-base leading-relaxed text-slate-700 mb-4">
              Hiro is a code architecture generator built for teams who think visually. Instead of
              staring at thousands of lines of Python, you get a clean flow of classes, methods, and
              function calls — similar to how a teacher would sketch the big picture on a board.
            </p>
            <p className="text-sm sm:text-base leading-relaxed text-slate-700">
              Use it to onboard new engineers faster, explain designs during reviews, or keep your
              documentation living alongside the code. Every diagram is generated from the real
              project so it never drifts out of date.
            </p>
          </div>
          <div className="rounded-2xl border border-dashed border-slate-300 bg-[#fdf8f0] px-5 py-4 text-xs sm:text-sm text-slate-700 shadow-sm">
            <p className="font-semibold mb-2 text-orange-700">What Hiro generates for you</p>
            <ul className="space-y-1 list-disc list-inside">
              <li>Mermaid diagrams ready to edit or share.</li>
              <li>Plain‑English architecture summaries of your modules.</li>
              <li>Clickable, zoomable views ideal for walkthroughs.</li>
            </ul>
          </div>
        </section>

        {/* Simple 3‑step strip */}
        <section className="space-y-6">
          <h2 className="text-2xl sm:text-3xl font-semibold text-slate-900">
            From repository to diagram in three steps.
          </h2>
          <div className="grid gap-5 md:grid-cols-3 text-sm sm:text-base">
            <StepCard number="1" title="Point Hiro at your code">
              Paste a local path or GitHub URL to any Python project you want to explore.
            </StepCard>
            <StepCard number="2" title="Watch the structure appear">
              We parse classes, methods, and function calls into a graph that mirrors your design.
            </StepCard>
            <StepCard number="3" title="Zoom, explain, and export">
              Present the diagram, read the generated explanation, and export to SVG or docs.
            </StepCard>
          </div>
        </section>

        {/* Call to action strip */}
        <section className="rounded-3xl border border-slate-300 bg-white/80 px-6 sm:px-8 py-7 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-[0_14px_30px_rgba(15,23,42,0.08)]">
          <div>
            <p className="text-sm font-semibold tracking-wide text-orange-700 mb-1">
              READY TO SEE YOUR CODE AS A DIAGRAM?
            </p>
            <p className="text-base sm:text-lg text-slate-800">
              Jump into the architecture generator and try it on a real repository.
            </p>
          </div>
          <Link
            to="/diagram-generator"
            className="inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-[#f9f5ee] shadow-md shadow-slate-500/40 hover:bg-slate-800 transition-colors"
          >
            Open Code Architecture Generator
            <span className="text-base">→</span>
          </Link>
        </section>
      </main>

      <footer className="border-t border-slate-300/60 bg-[#f7efe2] mt-10">
        <div className="max-w-6xl mx-auto px-6 sm:px-10 py-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs sm:text-sm text-slate-600">
          <p>© 2026 Hiro — Code Architecture Generator.</p>
          <p className="text-[11px]">
            Built for engineers who think in diagrams, not walls of code.
          </p>
        </div>
      </footer>
    </div>
  );
}

function StepCard({ number, title, children }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">
      <div className="mb-2 inline-flex h-6 w-6 items-center justify-center rounded-md bg-orange-500 text-[11px] font-bold text-[#fdf8f0]">
        {number}
      </div>
      <h3 className="mb-1 text-sm font-semibold text-slate-900">{title}</h3>
      <p className="text-xs sm:text-sm text-slate-700">{children}</p>
    </div>
  );
}

