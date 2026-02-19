import { formatDocumentation } from './formatDocumentation';

export const generateArchitectureReport = (mermaidCode, documentation) => {
    const date = new Date().toLocaleDateString();

    const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hiro Architecture Report</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({
            startOnLoad: true,
            theme: 'dark',
            securityLevel: 'loose',
        });
    </script>
    <style>
        body {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background-color: #0f172a;
            color: #e2e8f0;
            margin: 0;
            padding: 40px;
            line-height: 1.6;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            margin-bottom: 60px;
            padding-bottom: 40px;
            border-bottom: 1px solid #334155;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(to right, #60a5fa, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .meta {
            color: #94a3b8;
            font-size: 0.9rem;
        }
        .section {
            background: #1e293b;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 40px;
            border: 1px solid #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }
        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 25px;
            color: #f8fafc;
            display: flex;
            align-items: center;
            gap: 10px;
            border-bottom: 1px solid #334155;
            padding-bottom: 15px;
        }
        .diagram-container {
            background: #0f172a;
            padding: 20px;
            border-radius: 8px;
            overflow: auto;
            display: flex;
            justify-content: center;
        }
        .docs-content {
            color: #cbd5e1;
        }
        .docs-content h3 {
            color: #60a5fa;
            font-size: 1.25rem;
            margin-top: 25px;
            margin-bottom: 15px;
            border-bottom: 1px solid #334155;
            padding-bottom: 5px;
        }
        .docs-content strong {
            color: #e2e8f0;
        }
        .docs-content ul {
            padding-left: 20px;
        }
        .docs-content li {
            margin-bottom: 8px;
            color: #94a3b8;
        }
        @media print {
            body { background: white; color: black; }
            .section { background: white; border: 1px solid #ddd; box-shadow: none; }
            h1 { -webkit-text-fill-color: black; }
            .diagram-container { background: white; border: 1px solid #eee; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Hiro Architecture Report</h1>
            <div class="meta">Generated on ${date} • Powered by Hiro AI</div>
        </header>

        <div class="section">
            <div class="section-title">
                <span>🎨</span> Architecture Diagram
            </div>
            <div class="diagram-container">
                <div class="mermaid">
${mermaidCode}
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">
                <span>📚</span> Code Analysis & Documentation
            </div>
            <div class="docs-content">
                ${formatDocumentation(documentation)} 
            </div>
        </div>
    </div>
</body>
</html>
    `;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `hiro-report-${new Date().toISOString().slice(0, 10)}.html`;
    link.click();
    URL.revokeObjectURL(url);
};

// End of file
