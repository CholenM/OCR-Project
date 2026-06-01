# OCR System Pipeline - Visual Documentation

## System Overview

```mermaid
graph TD
    subgraph UserInterface[Streamlit UI Dashboard]
        UIDash[OCR Dashboard] --> Auth[Authentication Panel]
        UIDash --> Upload[Document Upload]
        UIDash --> Results[Results Preview]
        UIDash --> Metrics[Usage Metrics]
        UIDash --> Integration[n8n Integration]
    end
    
    subgraph Backend[FastAPI Backend Service]
        API[REST API Endpoints] --> Val[Key Validation]
        API --> OCRProc[OCR Processing]
        API --> MetricsDB[Metrics Database]
        API --> Audit[Audit Logging]
    end
    
    subgraph External[External Services]
        LM[LM Studio OCR Engine] --> Paddle[PaddleOCR-VL-1.5]
        n8n[n8n Workflow] --> Vector[Vector Store]
    end
    
    UserInterface -->|HTTP Requests| Backend
    Backend -->|OCR Jobs| LM
    Backend -->|Webhook| n8n
    Results -->|Optional| n8n
    
    style UserInterface fill:#f9f,stroke:#333
    style Backend fill:#bbf,stroke:#333
    style External fill:#9f9,stroke:#333
```

## Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant FastAPI
    
    User->>Streamlit: Enters API Key
    Streamlit->>FastAPI: GET /v1/metrics
    FastAPI->>FastAPI: Validate API Key
    alt Valid Key
        FastAPI-->>Streamlit: 200 OK with Metrics
        Streamlit->>User: Display Dashboard
    else Invalid Key
        FastAPI-->>Streamlit: 401 Unauthorized
        Streamlit->>User: Show Error
    else Deactivated Account
        FastAPI-->>Streamlit: 403 Forbidden
        Streamlit->>User: Show Error
    else Quota Exceeded
        FastAPI-->>Streamlit: 402 Payment Required
        Streamlit->>User: Show Error
    end
```

## Document Processing Pipeline

```mermaid
flowchart TD
    subgraph Upload[Document Upload]
        A[User Uploads File] --> B{File Type?}
        B -->|PDF| C[Configure DPI]
        B -->|Image| D[Skip Configuration]
        C --> E[Choose Mode: Serial/Concurrent]
        D --> E
        E --> F[Click Execute OCR]
    end
    
    subgraph Processing[FastAPI Processing]
        F --> G[Validate API Key]
        G --> H{File Type?}
        H -->|PDF| I[Extract Pages with PyMuPDF]
        H -->|Image| J[Encode as Base64]
        I --> K[Convert Each Page to JPEG]
        K --> L[Encode Pages as Base64]
        J --> M
        L --> M{Processing Mode?}
        M -->|Serial| N[Process Pages Sequentially]
        M -->|Concurrent| O[Async Processing with Semaphore]
        N --> P[Send to LM Studio]
        O --> P
        P --> Q[Receive Markdown + Tokens]
        Q --> R[Normalize Tables]
        R --> S[Calculate Metrics]
        S --> T[Update Database]
        T --> U[Return Markdown Response]
    end
    
    subgraph Results[Streamlit Results]
        U --> V[Display Success Message]
        V --> W[Show Download Button]
        W --> X[Display Raw Markdown]
        X --> Y[Display Rendered Preview]
    end
    
    style Upload fill:#f96,stroke:#333
    style Processing fill:#69f,stroke:#333
    style Results fill:#9f6,stroke:#333
```

## OCR Processing Modes Comparison

```mermaid
stateDiagram-v2
    [*] --> ModeSelection
    
    state ModeSelection {
        [*] --> Decision
        Decision: Processing Mode
        Decision --> Serial: Choose Serial
        Decision --> Concurrent: Choose Concurrent
    }
    
    state Serial {
        [*] --> Page1
        Page1 --> Page2
        Page2 --> Page3
        Page3 --> [*]
        
        note right of Serial
            Pros:
            - Lower memory usage
            - More stable
            - Predictable performance
            
            Cons:
            - Slower for multi-page docs
        end note
    }
    
    state Concurrent {
        [*] --> Fork
        Fork --> Page1
        Fork --> Page2
        Fork --> Page3
        Page1 --> Join
        Page2 --> Join
        Page3 --> Join
        Join --> [*]
        
        note left of Concurrent
            Pros:
            - Faster processing
            - Better hardware utilization
            - Configurable concurrency (1-8)
            
            Cons:
            - Higher memory usage
            - More complex error handling
        end note
    }
    
    ModeSelection --> Serial
    ModeSelection --> Concurrent
```

## LM Studio Integration

```mermaid
sequenceDiagram
    participant FastAPI
    participant LMStudio
    
    FastAPI->>LMStudio: POST /v1/chat/completions
    activate LMStudio
    Note right of FastAPI: Request includes:
    Note right of FastAPI: - Base64 encoded image
    Note right of FastAPI: - System prompt for OCR
    Note right of FastAPI: - Temperature = 0.0
    
    LMStudio->>LMStudio: Process with PaddleOCR-VL-1.5
    LMStudio-->>FastAPI: Response with:
    activate FastAPI
    Note left of LMStudio: - Extracted Markdown
    Note left of LMStudio: - Prompt tokens
    Note left of LMStudio: - Completion tokens
    deactivate LMStudio
    
    FastAPI->>FastAPI: Normalize tables
    FastAPI->>FastAPI: Calculate metrics
    deactivate FastAPI
```

## Metrics & Billing Flow

```mermaid
graph LR
    subgraph Database[API Key Database]
        User1[legal_team_secret_abc123] --> Metrics1[metrics]
        User1 --> Logs1[audit_logs]
        User2[test_key_0000] --> Metrics2[metrics]
        User2 --> Logs2[audit_logs]
    end
    
    subgraph Metrics
        Metrics1 --> Docs[total_documents: 5]
        Metrics1 --> Pages[total_pages: 42]
        Metrics1 --> Tokens[total_tokens: 12500]
        Metrics1 --> Spend[current_month_spend: $25.50]
    end
    
    subgraph AuditLogs
        Logs1 --> Entry1[timestamp, filename, pages]
        Logs1 --> Entry2[tokens, latency, cost]
        Logs1 --> Entry3[speed_tps]
    end
    
    FastAPI -->|Read/Write| Database
    Streamlit -->|GET /v1/metrics| FastAPI
    FastAPI -->|Response| Streamlit
    Streamlit -->|Display| Dashboard
    
    style Database fill:#f96,stroke:#333
    style Metrics fill:#6f6,stroke:#333
    style AuditLogs fill:#66f,stroke:#333
```

## n8n Integration Flow

```mermaid
sequenceDiagram
    participant User
    participant Streamlit
    participant n8n
    participant VectorStore
    
    User->>Streamlit: Enters n8n Webhook URL
    User->>Streamlit: Clicks "Upload to Vector Store"
    Streamlit->>n8n: POST to Webhook
    activate n8n
    Note right of Streamlit: Payload includes:
    Note right of Streamlit: - filename
    Note right of Streamlit: - markdown_content
    Note right of Streamlit: - timestamp
    
    n8n->>VectorStore: Process and Store
    activate VectorStore
    VectorStore-->>n8n: Confirmation
    deactivate VectorStore
    n8n-->>Streamlit: 200 Success
    deactivate n8n
    Streamlit->>User: Show Success Message
```

## Error Handling Flow

```mermaid
flowchart TD
    A[User Action] --> B[Streamlit Request]
    B --> C{FastAPI Response}
    
    C -->|200 OK| D[Success Path]
    C -->|400 Bad Request| E[Show: Invalid parameters]
    C -->|401 Unauthorized| F[Show: Invalid API Key]
    C -->|402 Payment Required| G[Show: Quota Exceeded]
    C -->|403 Forbidden| H[Show: Account Deactivated]
    C -->|500 Server Error| I[Show: Processing Exception]
    
    D --> J[Display Results]
    E --> K[Prompt for Correction]
    F --> L[Redirect to Auth]
    G --> M[Contact IT Message]
    H --> N[Contact Support Message]
    I --> O[Retry Option]
    
    style D fill:#9f9,stroke:#333
    style E fill:#f99,stroke:#333
    style F fill:#f99,stroke:#333
    style G fill:#f99,stroke:#333
    style H fill:#f99,stroke:#333
    style I fill:#f99,stroke:#333
```

## Performance Metrics Visualization

```mermaid
gauge
    title Processing Performance
    gauge "Tokens per Second" 85 0 100
    gauge "Concurrency Level" 3 0 8
    gauge "DPI Setting" 200 72 400
    gauge "Memory Usage" 60 0 100
```

## Complete System Flow

```mermaid
flowchart TB
    subgraph UserInterface
        UI1[Login with API Key] --> UI2[Upload Document]
        UI2 --> UI3[Configure Settings]
        UI3 --> UI4[Execute OCR]
        UI4 --> UI5[View Results]
        UI5 --> UI6[Optional: Export to n8n]
    end
    
    subgraph BackendService
        BE1[Validate API Key] --> BE2[Process Document]
        BE2 --> BE3[Send to LM Studio]
        BE3 --> BE4[Receive Markdown]
        BE4 --> BE5[Normalize Tables]
        BE5 --> BE6[Update Metrics]
        BE6 --> BE7[Return Response]
    end
    
    subgraph ExternalServices
        ES1[LM Studio OCR] --> ES2[n8n Workflow]
        ES2 --> ES3[Vector Store]
    end
    
    UI1 -->|API Key| BE1
    UI4 -->|Document| BE2
    BE3 -->|OCR Request| ES1
    BE7 -->|Markdown| UI5
    UI6 -->|Webhook| ES2
    
    style UserInterface fill:#f96,stroke:#333
    style BackendService fill:#69f,stroke:#333
    style ExternalServices fill:#9f9,stroke:#333
```

## Key Features Summary

### Processing Capabilities
- **File Types**: PDF, JPG, PNG
- **DPI Range**: 120-350 (default 200)
- **Processing Modes**: Serial or Concurrent
- **Concurrency**: 1-8 parallel pages (default 3)

### Table Recovery
- Two-pass OCR extraction
- Markdown table normalization
- Consistent column counts
- Empty cell filling

### Financial Controls
- Per-key monthly spend caps
- Real-time spend tracking
- Automatic quota enforcement
- Detailed cost auditing

### Monitoring & Telemetry
- Processing time tracking
- Tokens per second metrics
- Comprehensive audit logs
- Per-document cost calculation

### Integration Points
- LM Studio OCR Engine (Primary)
- n8n Workflow Automation (Optional)
- Vector Store (via n8n)
