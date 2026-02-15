import React from 'react';

const AnalysisPanel = ({ data }) => {
    if (!data) return <div className="text-gray-500 text-center py-10">No analysis data available</div>;

    return (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <h3 className="text-xl font-bold text-gray-200 mb-6 flex items-center gap-2">
                <span className="text-2xl">📊</span> Code Analysis
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Summary Card */}
                <div className="bg-gray-800/50 rounded-lg p-5 border border-gray-700">
                    <div className="text-gray-400 text-sm mb-1">Total Files</div>
                    <div className="text-3xl font-bold text-white mb-2">{data.fileCount}</div>
                    <div className="text-xs text-gray-500">Across {data.languages?.length || 0} languages</div>
                </div>

                {/* Complexity Card */}
                <div className="bg-gray-800/50 rounded-lg p-5 border border-gray-700">
                    <div className="text-gray-400 text-sm mb-1">Complexity Score</div>
                    <div className={`text-3xl font-bold mb-2 ${data.complexity === 'High' ? 'text-red-400' :
                            data.complexity === 'Medium' ? 'text-yellow-400' : 'text-green-400'
                        }`}>
                        {data.complexity}
                    </div>
                    <div className="text-xs text-gray-500">Based on cyclomatic complexity</div>
                </div>

                {/* Maintainability Card */}
                <div className="bg-gray-800/50 rounded-lg p-5 border border-gray-700">
                    <div className="text-gray-400 text-sm mb-1">Maintainability</div>
                    <div className="text-3xl font-bold text-blue-400 mb-2">{data.maintainability || 'A'}</div>
                    <div className="text-xs text-gray-500">Estimated grade</div>
                </div>
            </div>

            <div className="mt-8">
                <h4 className="text-lg font-semibold text-gray-300 mb-4">Language Breakdown</h4>
                <div className="space-y-3">
                    {data.languages && data.languages.map((lang, index) => (
                        <div key={index} className="flex items-center gap-4">
                            <div className="w-24 text-gray-400 text-sm">{lang}</div>
                            <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-blue-500 rounded-full"
                                    style={{ width: `${100 / data.languages.length}%` }}
                                ></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AnalysisPanel;
