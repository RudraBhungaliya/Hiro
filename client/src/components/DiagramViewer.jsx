import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';

mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  securityLevel: 'loose',
});

const DiagramViewer = ({ chart }) => {
  const [svgContent, setSvgContent] = useState('');
  const wrapperRef = useRef(null);
  const controlsRef = useRef(null);

  useEffect(() => {
    if (!chart) return;

    const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;

    mermaid
      .render(id, chart)
      .then(({ svg }) => setSvgContent(svg))
      .catch((err) => {
        console.error('Mermaid render error:', err);
        setSvgContent('');
      });
  }, [chart]);

  // Center and slightly offset the diagram after SVG is available
  useEffect(() => {
    if (!svgContent || !wrapperRef.current || !controlsRef.current) return;

    const { centerView, setTransform } = controlsRef.current;

    const timeout = setTimeout(() => {
      centerView(1.4);

      const innerTimeout = setTimeout(() => {
        const state = wrapperRef.current.instance.transformState;
        setTransform(state.positionX, state.positionY - 80, state.scale);
      }, 80);

      return () => clearTimeout(innerTimeout);
    }, 140);

    return () => clearTimeout(timeout);
  }, [svgContent]);

  if (!chart) {
    return (
      <div className="w-full p-6 bg-gray-900/80 rounded-2xl border border-gray-800 min-h-[420px] flex flex-col items-center justify-center text-gray-500 gap-2">
        <span className="text-4xl">🧩</span>
        <p className="text-sm">No diagram generated yet. Run an analysis to see your architecture.</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-[88vh] rounded-2xl border border-gray-800 bg-gradient-to-b from-gray-950 via-slate-950 to-black overflow-hidden">
      <div className="pointer-events-none absolute inset-0 opacity-40 bg-[radial-gradient(circle_at_1px_1px,#111827_1px,transparent_0)] bg-[length:26px_26px]" />

      <TransformWrapper
        ref={wrapperRef}
        minScale={0.3}
        maxScale={5}
        limitToBounds
        centerZoomedOut
      >
        {(controls) => {
          controlsRef.current = controls;
          const { zoomIn, zoomOut, resetTransform, centerView } = controls;

          return (
            <>
              <div className="absolute top-4 right-4 z-20 flex items-center gap-2 bg-gray-900/80 border border-gray-700/70 rounded-full px-3 py-1.5 shadow-xl shadow-black/40 backdrop-blur">
                <span className="hidden md:inline text-xs font-medium text-gray-400 mr-1">
                  View
                </span>
                <button
                  onClick={() => zoomOut()}
                  className="w-7 h-7 flex items-center justify-center rounded-full bg-gray-800 hover:bg-gray-700 text-gray-200 text-sm transition-colors"
                  title="Zoom out"
                >
                  −
                </button>
                <button
                  onClick={() => zoomIn()}
                  className="w-7 h-7 flex items-center justify-center rounded-full bg-gray-800 hover:bg-gray-700 text-gray-200 text-sm transition-colors"
                  title="Zoom in"
                >
                  +
                </button>
                <button
                  onClick={() => centerView(1.4)}
                  className="w-7 h-7 flex items-center justify-center rounded-full bg-gray-800 hover:bg-gray-700 text-gray-200 text-[11px] transition-colors"
                  title="Center diagram"
                >
                  ⟲
                </button>
                <button
                  onClick={() => resetTransform()}
                  className="hidden sm:flex w-20 h-7 items-center justify-center rounded-full bg-gray-800 hover:bg-gray-700 text-gray-200 text-[11px] font-medium transition-colors"
                  title="Reset view"
                >
                  Reset
                </button>
              </div>

              <TransformComponent wrapperClass="w-full h-full">
                <div className="relative w-full h-full flex items-center justify-center p-10">
                  <div className="min-w-[1100px] min-h-[700px] flex items-start justify-center pt-52">
                    <div
                      className="mermaid-diagram bg-gray-900/90 rounded-2xl border border-gray-800/80 shadow-2xl shadow-black/50 px-10 py-8"
                      dangerouslySetInnerHTML={{ __html: svgContent }}
                    />
                  </div>
                </div>
              </TransformComponent>
            </>
          );
        }}
      </TransformWrapper>
    </div>
  );
};

export default DiagramViewer;
