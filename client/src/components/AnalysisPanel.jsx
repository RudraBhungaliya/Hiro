import React, { useMemo } from 'react';
import { formatDocumentation } from '../utils/formatDocumentation';


const AnalysisPanel = ({ data }) => {
    // data is expected to be the documentation string
    const docString = typeof data === 'string' ? data : '';
    const formattedDocs = useMemo(() => formatDocumentation(docString), [docString]);

    if (!docString) return (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-8 text-center">
            <div className="text-gray-500">No documentation available</div>
        </div>
    );

    return (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-8 shadow-2xl">
            <h3 className="text-2xl font-bold text-gray-200 mb-6 flex items-center gap-3 border-b border-gray-800 pb-4">
                <span className="text-3xl">📚</span> Project Documentation
            </h3>

            <div
                className="prose prose-invert max-w-none text-gray-300 leading-relaxed"
                dangerouslySetInnerHTML={{ __html: formattedDocs }}
            />
        </div>
    );
};

export default AnalysisPanel;
