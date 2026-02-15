export const MOCK_ANALYSIS_RESPONSE = {
    mermaid: `graph TD
      Client[Client] -->|HTTP| API[API Gateway]
      API --> Auth[Auth Service]
      API --> Product[Product Service]
      API --> Order[Order Service]
      Auth --> DB[(Database)]
      Product --> DB
      Order --> DB
      Order --> Payment[Payment Service]
      `,
    analysis: {
        fileCount: 42,
        complexity: "Medium",
        maintainability: "B+",
        languages: ["JavaScript", "Python", "CSS"]
    },
    insights: [
        { type: "warning", message: "High coupling detected between Order Service and Payment Service" },
        { type: "info", message: "Consider adding caching to Product Service for better performance" },
        { type: "success", message: "Auth Service has good test coverage" },
        { type: "error", message: "Circular dependency detected in Utils module" }
    ]
};
