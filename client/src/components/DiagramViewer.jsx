import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

mermaid.initialize({
    startOnLoad: true,
    theme: 'dark',
    securityLevel: 'loose',
});

const DiagramViewer = ({ chart }) => {
    const [svgContent, setSvgContent] = useState('');
    const wrapperRef = useRef(null);

    useEffect(() => {
        if (!chart) return;

        const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;

        mermaid.render(id, chart)
            .then(({ svg }) => setSvgContent(svg))
            .catch(err => console.error(err));
    }, [chart]);

    if (!chart) {
        return (
            <div className="w-full p-4 bg-gray-900 rounded-lg border border-gray-700 min-h-[400px] flex items-center justify-center text-gray-500">
                No diagram generated yet
            </div>
        );
    }

    return (
        <div className="w-full h-[88vh] bg-gray-900 rounded-lg border border-gray-700 overflow-hidden relative">

            <TransformWrapper
                ref={wrapperRef}
                minScale={0.4}
                maxScale={5}
                limitToBounds={true}
                centerZoomedOut={true}
            >
                {({ zoomIn, zoomOut, resetTransform, centerView, setTransform }) => {

                    // ⭐ Perfect centering after diagram renders
                    useEffect(() => {
                        if (!svgContent) return;

                        setTimeout(() => {
                            // Step 1 — let library perfectly center the diagram
                            centerView(1.6);   // scale = starting zoom

                            // Step 2 — move camera slightly up (10% spacing)
                            setTimeout(() => {
                                const state = wrapperRef.current.instance.transformState;
                                setTransform(state.positionX, state.positionY - 80, state.scale);
                            }, 50);

                        }, 120);

                    }, [svgContent]);

                    return (
                        <>
                            <div className="absolute top-4 right-4 z-10 flex flex-col gap-2">
                                <button onClick={zoomIn} className="bg-gray-800 p-2 rounded text-white">+</button>
                                <button onClick={zoomOut} className="bg-gray-800 p-2 rounded text-white">−</button>
                                <button onClick={() => centerView(1.6)} className="bg-gray-800 p-2 rounded text-white">⟲</button>
                            </div>

                            <TransformComponent wrapperClass="w-full h-full">
                                <div className="min-w-[2200px] min-h-[1400px] flex justify-center pt-[10vh]">
                                    <div
                                        className="mermaid-diagram"
                                        dangerouslySetInnerHTML={{ __html: svgContent }}
                                    />
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
