import React, { useEffect, useState } from 'react';
import mermaid from 'mermaid';
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

mermaid.initialize({
    startOnLoad: true,
    theme: 'dark',
    securityLevel: 'loose',
});

const DiagramViewer = ({ chart }) => {
    const [svgContent, setSvgContent] = useState('');

    useEffect(() => {
        if (chart) {
            const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;

            try {
                mermaid.render(id, chart).then(({ svg }) => {
                    setSvgContent(svg);
                });
            } catch (error) {
                console.error("Mermaid error:", error);
                setSvgContent(`<div class="text-red-500">Error rendering diagram: ${error.message}</div>`);
            }
        }
    }, [chart]);

    if (!chart) {
        return (
            <div className="diagram-viewer w-full p-4 bg-gray-900 rounded-lg shadow-xl border border-gray-700 min-h-[400px] flex items-center justify-center text-gray-500">
                No diagram generated yet
            </div>
        )
    }

    return (
        <div className="diagram-viewer w-full h-[600px] bg-gray-900 rounded-lg shadow-xl border border-gray-700 overflow-hidden relative">
            <TransformWrapper
                initialScale={1}
                minScale={0.5}
                maxScale={4}
                centerOnInit={true}
            >
                {({ zoomIn, zoomOut, resetTransform }) => (
                    <>
                        <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
                            <button onClick={() => zoomIn()} className="bg-gray-800 p-2 rounded hover:bg-gray-700 text-white shadow-lg border border-gray-700" title="Zoom In">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                            </button>
                            <button onClick={() => zoomOut()} className="bg-gray-800 p-2 rounded hover:bg-gray-700 text-white shadow-lg border border-gray-700" title="Zoom Out">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                                </svg>
                            </button>
                            <button onClick={() => resetTransform()} className="bg-gray-800 p-2 rounded hover:bg-gray-700 text-white shadow-lg border border-gray-700" title="Reset">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                            </button>
                        </div>

                        <TransformComponent wrapperClass="w-full h-full" contentClass="w-full h-full flex items-center justify-center">
                            <div
                                className="w-full h-full flex items-center justify-center"
                                dangerouslySetInnerHTML={{ __html: svgContent }}
                            />
                        </TransformComponent>
                    </>
                )}
            </TransformWrapper>
        </div>
    );
};

export default DiagramViewer;
