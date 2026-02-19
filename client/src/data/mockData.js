export const MOCK_ANALYSIS_RESPONSE = {
    diagram: `flowchart LR
    User[User Browser] --> CDN[CDN / Edge]
    CDN --> LB[Load Balancer]

    LB --> FE[Frontend Service]
    FE --> API[API Gateway]

    API --> Auth[Auth Service]
    API --> Product[Product Service]
    API --> Order[Order Service]
    API --> Payment[Payment Service]
    API --> Notification[Notification Service]

    Auth --> Redis[(Redis Cache)]
    Product --> DB1[(Product DB)]
    Order --> DB2[(Order DB)]
    Payment --> Stripe[Stripe API]

    Order --> MQ[(Message Queue)]
    MQ --> Worker[Background Worker]
    Worker --> Email[Email Service]
    Worker --> Analytics[Analytics Service]

    Analytics --> DataLake[(Data Lake)]

    Dev[Developer] --> Git[GitHub]
    Git --> CI[CI Pipeline]
    CI --> Docker[Docker Build]
    Docker --> Registry[Container Registry]
    Registry --> K8s[Kubernetes Cluster]

    K8s --> FE
    K8s --> API
`,
    documentation: `Overview:
This codebase appears to be a part of an e-commerce application, responsible for user management, order processing, and payment handling. It provides a range of services that interact with each other to facilitate business logic. The system seems to follow a modular design.

Components:
• UserService — Manages user registration, login, account deletion, and password reset, depending on AuthService, Database, and EmailService.
• OrderService — Handles order-related operations such as placing orders, canceling orders, and retrieving order information, depending on UserService, Database, and EmailService.
• PaymentService — Processes payments and handles refunds, depending on OrderService, Database, and EmailService.
• AuthService — Generates tokens for authentication, validates tokens, and revokes tokens, depending on no external services.
• EmailService — Sends welcome emails, rese t password notifications, and other email-related communications, depending on no external services.
• Database — Provides basic CRUD operations such as saving data, retrieving data, and deleting data, depending on no external services.

Architecture Pattern:
The codebase follows a Service-Oriented Architecture (SOA) pattern, where each service is designed to be independent and loosely coupled with other services.`
};    
