import React from 'react';

const InsightsPanel = ({ data }) => {
    if (!data || data.length === 0) return <div className="text-gray-500 text-center py-10">No insights available</div>;

    const getIcon = (type) => {
        switch (type) {
            case 'warning': return '⚠️';
            case 'error': return '🚫';
            case 'success': return '✅';
            default: return '💡';
        }
    };

    const getColor = (type) => {
        switch (type) {
            case 'warning': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20';
            case 'error': return 'bg-red-500/10 text-red-400 border-red-500/20';
            case 'success': return 'bg-green-500/10 text-green-400 border-green-500/20';
            default: return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
        }
    };

    return (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <h3 className="text-xl font-bold text-gray-200 mb-6 flex items-center gap-2">
                <span className="text-2xl">⚡</span> Automated Insights
            </h3>

            <div className="space-y-4">
                {data.map((insight, index) => (
                    <div
                        key={index}
                        className={`p-4 rounded-lg border flex items-start gap-4 ${getColor(insight.type)}`}
                    >
                        <div className="text-xl mt-1">{getIcon(insight.type)}</div>
                        <div>
                            <h4 className="font-semibold mb-1 capitalize">{insight.type}</h4>
                            <p className="text-sm opacity-90">{insight.message}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default InsightsPanel;
