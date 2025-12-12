# Integration Landscape & Data Flow Documentation

This document provides a visual and tabular representation of the system's integration landscape, focusing on data flows, data sensitivity (PII), and security controls.

## Recommended Tools & Notation

*   **Notation**: [C4 Model](https://c4model.com/) (Context, Container, Component, Code) for architectural diagrams.
*   **Tools**: [Mermaid.js](https://mermaid.js.org/) for defining diagrams as code within Markdown. This allows for version control and easy rendering in GitHub/GitLab/IDEs.
*   **Format**: Markdown tables for the detailed integration catalog.

## 1. Visual Landscape (C4 Container Diagram)

The following diagram illustrates the high-level containers and their interactions.

```mermaid
C4Context
    title System Integration Landscape - Product Catalog & Inventory

    %% Actors
    Person(customer, "Customer", "A user of the e-commerce platform")
    Person(admin, "Administrator", "Internal user managing products")

    %% System Boundary
    System_Boundary(ecommerce, "E-Commerce System") {
        
        %% Product Catalog Subsystem
        Container(prodCatApi, "Product Catalog API", "Node.js/Express", "Manages product data")
        ContainerDb(prodCatDb, "Product Catalog DB", "MongoDB", "Stores product information")
        
        %% Product Inventory Subsystem
        Container(invApi, "Product Inventory API", "Node.js/Express", "Manages stock levels")
        ContainerDb(invDb, "Product Inventory DB", "MongoDB", "Stores inventory counts")

        %% Internal Relations
        Rel(prodCatApi, prodCatDb, "Reads/Writes", "MongoDB Protocol/TCP 27017")
        Rel(invApi, invDb, "Reads/Writes", "MongoDB Protocol/TCP 27017")
        Rel(prodCatApi, invApi, "Queries Stock", "HTTPS/JSON")
    }

    %% External Systems
    System_Ext(telemetry, "Telemetry Collector", "Datadog Agent/OTLP", "Collects traces and metrics")
    System_Ext(canvas, "Canvas Info", "Service Discovery", "Provides environment info")

    %% External Relations
    Rel(customer, prodCatApi, "Views Products", "HTTPS")
    Rel(admin, prodCatApi, "Updates Products", "HTTPS")
    
    Rel(prodCatApi, telemetry, "Sends Traces", "OTLP/HTTP")
    Rel(prodCatApi, canvas, "Fetches Config", "HTTP")
```

## 2. Integration & Data Flow Catalog

This table details the specific data flows, highlighting security and compliance aspects.

| ID | Source Component | Target Component | Protocol / Interface | Data Description | Data Classification / PII | Security Controls & Concerns |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **INT-001** | `ProductCatalogAPI` | `MongoDB` | TCP / 27017 (Mongo Wire) | Product details, descriptions, prices. | **Internal**. No PII in catalog data usually. | **Concern**: Unencrypted storage? <br> **Control**: TLS enabled, Auth enabled. |
| **INT-002** | `ProductCatalogAPI` | `OTLP Collector` | HTTP / 4318 | Application traces, performance metrics. | **Internal**. Potential incidental PII in logs? | **Concern**: Data leakage in logs. <br> **Control**: Log sanitization filters. |
| **INT-003** | `Customer` | `ProductCatalogAPI` | HTTPS / 443 | GET requests for product lists. | **Public**. | **Concern**: DDoS, Scraping. <br> **Control**: Rate limiting, WAF. |
| **INT-004** | `Admin` | `ProductCatalogAPI` | HTTPS / 443 | POST/PUT product updates. | **Confidential**. | **Concern**: Unauthorized changes. <br> **Control**: OAuth2/OIDC, RBAC (Role: Admin). |
| **INT-005** | `ProductCatalogAPI` | `CanvasInfo` | HTTP | Service discovery/config data. | **Internal**. | **Concern**: Internal network trust. |

## 3. Detailed Data Flow (Sequence Diagram)

For critical flows (e.g., involving PII or financial data), use a sequence diagram.

### Scenario: Product Update by Admin

```mermaid
sequenceDiagram
    autonumber
    participant Admin
    participant Gateway
    participant ProdCatAPI as Product Catalog API
    participant DB as MongoDB
    participant Audit as Audit Log (Hypothetical)

    Note over Admin, Gateway: Authenticated Session (OIDC)

    Admin->>Gateway: POST /products (Product Data)
    Gateway->>Gateway: Validate Token
    Gateway->>ProdCatAPI: Forward Request
    
    ProdCatAPI->>ProdCatAPI: Validate Input (Sanitization)
    
    ProdCatAPI->>DB: Insert Product Document
    DB-->>ProdCatAPI: Success (ID)
    
    par Async Logging
        ProdCatAPI->>Audit: Log Action (User ID, Timestamp, ProductID)
    end
    
    ProdCatAPI-->>Gateway: 201 Created
    Gateway-->>Admin: 201 Created
```

## How to use this template

1.  **Map your components**: Update the Mermaid C4 diagram with your actual microservices from `charts/` (e.g., `partyroleapi`, `promotionmanagementapi`).
2.  **Audit Data Types**: Fill the "Data Classification" column in the table. Tag fields as `PII`, `PCI`, `Public`, `Internal`, or `Confidential`.
3.  **Identify Risks**: Consult with InfoSec to fill the "Security Controls & Concerns" column.
