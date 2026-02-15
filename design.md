# Design Document: Codebase Architecture Visualizer

## Overview

The Codebase Architecture Visualizer is a web application that automatically analyzes codebases and generates interactive architecture diagrams. The system consists of a frontend web interface, a backend API server, a codebase analyzer module, an LLM integration layer, and a diagram rendering engine. The application accesses the user's workspace automatically, sends relevant code context to Anthropic's Claude API, and renders the resulting architecture diagrams in multiple formats.

## Architecture

The system follows a client-server architecture with the following layers:

```
┌─────────────────────────────────────────────────────────┐
│                    Web Frontend                         │
│  (React/Vue - Interactive UI, Diagram Viewer, Export)   │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────┐
│                    Backend API Server                   │
│         (Node.js/Python - REST API, WebSocket)          │
└─────────────────────────────────────────────────────────┘
                          ↕
        ┌─────────────────┴─────────────────┐
        ↓                                     ↓
┌──────────────────┐              ┌──────────────────────┐
│ Codebase Analyzer│              │  LLM Integration     │
│  (File Scanner,  │              │  (Claude API Client, │
│   Parser, Filter)│              │   Prompt Builder)    │
└──────────────────┘              └──────────────────────┘
        ↓                                     ↓
┌──────────────────┐              ┌──────────────────────┐
│  Local Workspace │              │   Anthropic Claude   │
│  (User's Files)  │              │       API            │
└──────────────────┘              └──────────────────────┘
                          ↓
                ┌──────────────────────┐
                │  Diagram Renderer    │
                │ (Mermaid, PlantUML,  │
                │  D3.js Support)      │
                └──────────────────────┘
```

## Components and Interfaces

### 1. Web Frontend

**Responsibilities:**
- Display user interface for triggering analysis
- Show progress indicators during analysis
- Render interactive architecture diagrams
- Provide export functionality
- Manage API key configuration

**Key Interfaces:**
```typescript
interface AnalysisRequest {
  workspacePath?: string;
  includePatterns?: string[];
  excludePatterns?: string[];
}

interface AnalysisResponse {
  diagramFormat: string;
  diagramCode: string;
  components: Component[];
  relationships: Relationship[];
  metadata: AnalysisMetadata;
}

interface Component {
  id: string;
  name: string;
  type: 'service' | 'database' | 'external_api' | 'module';
  description?: string;
  technologies?: string[];
}

interface Relationship {
  from: string;
  to: string;
  type: 'calls' | 'reads' | 'writes' | 'depends_on';
  description?: string;
}

interface ExportRequest {
  format: 'png' | 'svg' | 'pdf' | 'source';
  diagramCode: string;
  diagramFormat: string;
}
```

### 2. Backend API Server

**Responsibilities:**
- Handle HTTP requests from frontend
- Coordinate between codebase analyzer and LLM integration
- Manage WebSocket connections for real-time progress updates
- Handle export requests
- Validate and store API keys securely

**Key Endpoints:**
```
POST /api/analyze
  - Triggers codebase analysis
  - Returns analysis results with diagram

GET /api/analysis/:id
  - Retrieves cached analysis results

POST /api/export
  - Exports diagram in requested format
  - Returns file or download URL

POST /api/config/api-key
  - Stores encrypted API key

WebSocket /ws/analysis
  - Real-time progress updates during analysis
```

### 3. Codebase Analyzer

**Responsibilities:**
- Scan workspace directory structure
- Filter files based on ignore patterns
- Identify key files (entry points, configs, package files)
- Extract file metadata and relationships
- Sample large codebases intelligently

**Key Functions:**
```typescript
interface CodebaseAnalyzer {
  scanWorkspace(path: string): Promise<FileTree>;
  filterFiles(files: FileTree, patterns: FilterPatterns): FileTree;
  identifyKeyFiles(files: FileTree): KeyFile[];
  extractFileContent(files: KeyFile[]): FileContent[];
  buildContextSummary(files: FileContent[]): ContextSummary;
}

interface FileTree {
  root: string;
  files: FileNode[];
  totalSize: number;
}

interface FileNode {
  path: string;
  name: string;
  type: 'file' | 'directory';
  size: number;
  extension?: string;
}

interface KeyFile {
  path: string;
  importance: number;
  reason: string;
  content?: string;
}

interface ContextSummary {
  structure: string;
  keyFiles: string[];
  technologies: string[];
  estimatedComplexity: 'low' | 'medium' | 'high';
}
```

**File Prioritization Strategy:**
1. Configuration files (package.json, requirements.txt, pom.xml, etc.)
2. Entry points (main.*, index.*, app.*, server.*)
3. Database configuration and models
4. API route definitions
5. Service/module definitions
6. README and documentation files

**Sampling Strategy for Large Codebases:**
- If total files < 100: analyze all files
- If total files < 500: analyze key files + 20% sample
- If total files >= 500: analyze key files only + prompt user for specific directories

### 4. LLM Integration Layer

**Responsibilities:**
- Build prompts for Claude API
- Send requests to Anthropic API
- Parse Claude's responses
- Handle rate limiting and retries
- Extract diagram format and code from responses

**Key Functions:**
```typescript
interface LLMIntegration {
  analyzeArchitecture(context: ContextSummary): Promise<ArchitectureAnalysis>;
  selectDiagramFormat(analysis: ArchitectureAnalysis): Promise<DiagramFormat>;
  generateDiagram(analysis: ArchitectureAnalysis, format: DiagramFormat): Promise<DiagramCode>;
}

interface ArchitectureAnalysis {
  services: Service[];
  databases: Database[];
  externalAPIs: ExternalAPI[];
  relationships: Relationship[];
  insights: string[];
}

interface DiagramFormat {
  format: 'mermaid' | 'plantuml' | 'd3' | 'custom';
  rationale: string;
}

interface DiagramCode {
  format: string;
  code: string;
  renderingHints?: Record<string, any>;
}
```

**Prompt Structure:**
```
System: You are an expert software architect analyzing codebases to create architecture diagrams.

User: Analyze this codebase and identify:
1. Services and their responsibilities
2. Databases and data stores
3. External API integrations
4. Relationships and data flow between components

Codebase Context:
- Structure: [directory tree]
- Key Files: [file summaries]
- Technologies: [detected technologies]

Please provide:
1. A list of architectural components
2. Relationships between components
3. The best diagram format for this architecture (Mermaid, PlantUML, or D3.js)
4. The complete diagram code in the chosen format
```

**API Configuration:**
- Model: claude-3-5-sonnet-20241022 (or latest)
- Max tokens: 4096
- Temperature: 0.3 (for consistent output)
- Retry strategy: Exponential backoff (1s, 2s, 4s)
- Timeout: 30 seconds per request

### 5. Diagram Renderer

**Responsibilities:**
- Render Mermaid diagrams
- Render PlantUML diagrams
- Render D3.js diagrams
- Provide interactive features (zoom, pan, hover)
- Export diagrams to various formats

**Supported Libraries:**
- Mermaid.js: For Mermaid format rendering
- PlantUML Server/Client: For PlantUML rendering
- D3.js: For custom D3 diagrams
- html2canvas + jsPDF: For PNG and PDF export
- SVG export: Native browser support

**Key Functions:**
```typescript
interface DiagramRenderer {
  render(code: string, format: DiagramFormat, container: HTMLElement): Promise<void>;
  enableInteractivity(diagram: RenderedDiagram): void;
  exportToPNG(diagram: RenderedDiagram): Promise<Blob>;
  exportToSVG(diagram: RenderedDiagram): Promise<Blob>;
  exportToPDF(diagram: RenderedDiagram): Promise<Blob>;
  exportSource(code: string): Blob;
}

interface RenderedDiagram {
  element: HTMLElement;
  format: string;
  interactive: boolean;
}
```

## Data Models

### Analysis Result
```typescript
interface AnalysisResult {
  id: string;
  timestamp: Date;
  workspacePath: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  progress: number;
  diagramFormat: string;
  diagramCode: string;
  components: Component[];
  relationships: Relationship[];
  metadata: {
    filesAnalyzed: number;
    totalFiles: number;
    analysisTime: number;
    llmTokensUsed: number;
  };
  error?: string;
}
```

### Configuration
```typescript
interface AppConfig {
  apiKey: string; // Encrypted
  workspacePath: string;
  excludePatterns: string[];
  includePatterns: string[];
  maxFilesAnalyzed: number;
  cacheEnabled: boolean;
  cacheTTL: number; // seconds
}
```

### Cache Entry
```typescript
interface CacheEntry {
  workspaceHash: string;
  result: AnalysisResult;
  createdAt: Date;
  expiresAt: Date;
}
```

## Correctness Properties


*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Workspace Access Properties

Property 1: Workspace detection
*For any* valid workspace path, when the system initializes, it should successfully detect and return the workspace location.
**Validates: Requirements 1.1**

Property 2: File reading without uploads
*For any* file within an accessible workspace, the system should be able to read its contents directly without requiring upload mechanisms.
**Validates: Requirements 1.2**

Property 3: Ignore pattern respect
*For any* workspace containing ignore patterns (gitignore, etc.), files matching those patterns should be excluded from the analyzed file list.
**Validates: Requirements 1.3**

### Language-Agnostic Analysis Properties

Property 4: Language-independent component identification
*For any* codebase regardless of programming language, the analysis should produce at least one identified component without failing due to language constraints.
**Validates: Requirements 2.1**

Property 5: Pattern-based detection
*For any* codebase containing standard naming patterns (e.g., files/directories with "service", "module", "controller"), these should be identified as components.
**Validates: Requirements 2.2**

Property 6: Cross-language integration detection
*For any* codebase containing database connection strings or API endpoint URLs, these should be identified regardless of the programming language used.
**Validates: Requirements 2.3**

Property 7: Unknown file type handling
*For any* file with an unknown or uncommon extension, the system should attempt analysis without throwing errors and should include it in the analysis if it contains relevant patterns.
**Validates: Requirements 2.4**

### LLM Integration Properties

Property 8: Complete context transmission
*For any* codebase analysis request, the payload sent to Claude should contain both file structure information and file contents for key files.
**Validates: Requirements 3.2, 3.3**

Property 9: Structured response parsing
*For any* valid Claude API response containing architectural information, the system should parse it into a structured format with components, relationships, and diagram code fields.
**Validates: Requirements 3.4**

Property 10: API error resilience
*For any* API rate limit or transient error, the system should retry the request with exponential backoff and not crash.
**Validates: Requirements 3.5**

Property 11: Retry exhaustion handling
*For any* API request that fails after all retry attempts, the system should return an error result with the failure reason rather than throwing an unhandled exception.
**Validates: Requirements 8.3**

### Diagram Generation Properties

Property 12: Complete component representation
*For any* analysis result containing identified services, databases, or external APIs, all of these components should appear in the generated diagram code.
**Validates: Requirements 4.1, 4.2, 4.3**

Property 13: Component type distinction
*For any* diagram containing multiple component types (services, databases, external APIs), each type should have distinct visual markers or styling in the diagram code.
**Validates: Requirements 4.4**

Property 14: Relationship representation
*For any* identified relationship between components, the diagram should include a connection with the relationship type information.
**Validates: Requirements 4.5**

### Format Selection Properties

Property 15: Format selection request
*For any* analysis request sent to Claude, the prompt should include a request for the LLM to select the optimal diagram format.
**Validates: Requirements 5.1**

Property 16: Format consistency
*For any* analysis result where Claude selects a diagram format, the generated diagram code should be valid syntax for that format.
**Validates: Requirements 5.2**

Property 17: Multi-format rendering support
*For any* diagram in Mermaid, PlantUML, or D3.js format, the renderer should process it without errors.
**Validates: Requirements 5.3**

Property 18: Unsupported format fallback
*For any* diagram in an unsupported or unrecognized format, the system should convert it to Mermaid format.
**Validates: Requirements 5.4**

Property 19: Rationale inclusion
*For any* analysis result, the output should include a non-empty rationale field explaining the format choice.
**Validates: Requirements 5.5**

### Interactive Visualization Properties

Property 20: Interactive component rendering
*For any* rendered diagram, all components should have event handlers attached for hover and click interactions.
**Validates: Requirements 6.1**

Property 21: Hover detail display
*For any* component in a rendered diagram, hovering over it should trigger the display of additional detail information.
**Validates: Requirements 6.2**

Property 22: Zoom and pan functionality
*For any* rendered diagram, zoom and pan operations should modify the diagram's transform properties without errors.
**Validates: Requirements 6.3**

Property 23: Connection highlighting
*For any* component in a rendered diagram, clicking it should visually highlight all connections related to that component.
**Validates: Requirements 6.4**

### Export Properties

Property 24: Multi-format export validity
*For any* rendered diagram, exporting to PNG, SVG, PDF, or source code format should produce a valid blob/string of the correct type.
**Validates: Requirements 7.1, 7.2, 7.3, 7.4**

Property 25: Export content preservation
*For any* diagram exported to an image format, the exported file should contain all components and connections present in the original rendered diagram.
**Validates: Requirements 7.5**

Property 26: Source code export round-trip
*For any* diagram, exporting the source code and then re-rendering it should produce an equivalent diagram.
**Validates: Requirements 7.4**

### Error Handling Properties

Property 27: Comprehensive error messaging
*For any* error condition (workspace access failure, API failure, rendering failure, invalid API key), the system should produce a clear error message describing the issue.
**Validates: Requirements 7.6, 8.1, 8.3, 9.4**

Property 28: Rendering fallback
*For any* diagram that fails to render, the system should display the raw diagram code as a fallback.
**Validates: Requirements 8.4**

Property 29: Error logging
*For any* error that occurs during analysis, rendering, or export, an entry should be added to the error log.
**Validates: Requirements 8.5**

Property 30: Progress indication
*For any* analysis operation in progress, the system should emit progress updates with increasing progress values.
**Validates: Requirements 8.6**

### Security Properties

Property 31: API key encryption
*For any* API key stored by the system, the stored value should be encrypted and not equal to the plain text key.
**Validates: Requirements 9.2**

Property 32: API key validation
*For any* invalid API key format, the system should reject it before storage and return a validation error.
**Validates: Requirements 9.3**

Property 33: API key confidentiality
*For any* log entry or error message generated by the system, it should not contain API key values.
**Validates: Requirements 9.5**

Property 34: API key CRUD operations
*For any* stored API key, the system should support update and delete operations that successfully modify or remove the key.
**Validates: Requirements 9.6**

### Performance Properties

Property 35: Large codebase sampling
*For any* codebase with more than 500 files, the system should analyze only a subset of files rather than all files.
**Validates: Requirements 10.1**

Property 36: Key file prioritization
*For any* codebase analysis, configuration files and entry points should appear earlier in the analysis input than regular source files.
**Validates: Requirements 10.2**

Property 37: Threshold-based prompting
*For any* codebase exceeding the file count threshold, the system should trigger a user prompt for directory selection.
**Validates: Requirements 10.3**

Property 38: Analysis result caching
*For any* codebase, if analyzed twice without changes, the second analysis should return cached results without making new LLM API calls.
**Validates: Requirements 10.4**

Property 39: Long-running progress updates
*For any* analysis operation taking longer than 10 seconds, the system should emit at least one progress update during execution.
**Validates: Requirements 10.5**

## Error Handling

### Error Categories

1. **Workspace Access Errors**
   - Permission denied
   - Path not found
   - Invalid workspace structure
   - Response: Clear error message with resolution steps

2. **LLM API Errors**
   - Rate limiting (429)
   - Authentication failure (401)
   - Timeout
   - Invalid response format
   - Response: Retry with exponential backoff, then error message

3. **Rendering Errors**
   - Invalid diagram syntax
   - Unsupported format
   - Browser compatibility issues
   - Response: Fallback to raw code display

4. **Export Errors**
   - Format conversion failure
   - File system errors
   - Memory constraints
   - Response: Error message with specific failure reason

### Error Recovery Strategies

**Retry Logic:**
```typescript
async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (attempt === maxRetries - 1) throw error;
      const delay = baseDelay * Math.pow(2, attempt);
      await sleep(delay);
    }
  }
  throw new Error('Max retries exceeded');
}
```

**Graceful Degradation:**
- If LLM fails: Show error, allow retry
- If rendering fails: Show raw diagram code
- If export fails: Offer alternative formats
- If workspace access fails: Allow manual path selection

## Testing Strategy

### Dual Testing Approach

The system will use both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of file parsing
- Edge cases (empty codebases, single-file projects)
- Error conditions (invalid API keys, malformed responses)
- Integration points between components
- UI component rendering with specific inputs

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs
- Comprehensive input coverage through randomization
- Invariants that must be maintained across operations

### Property-Based Testing Configuration

**Library Selection:**
- TypeScript/JavaScript: fast-check
- Python: Hypothesis

**Test Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with: **Feature: codebase-architecture-visualizer, Property {N}: {property text}**
- Randomized inputs: file structures, component counts, relationship types

**Example Property Test Structure:**
```typescript
import fc from 'fast-check';

// Feature: codebase-architecture-visualizer, Property 3: Ignore pattern respect
test('files matching ignore patterns are excluded', () => {
  fc.assert(
    fc.property(
      fc.array(fc.string()), // file paths
      fc.array(fc.string()), // ignore patterns
      (files, patterns) => {
        const filtered = filterFiles(files, patterns);
        const shouldBeIgnored = files.filter(f => 
          patterns.some(p => f.includes(p))
        );
        return shouldBeIgnored.every(f => !filtered.includes(f));
      }
    ),
    { numRuns: 100 }
  );
});
```

### Test Coverage Goals

- Unit test coverage: >80% of code paths
- Property test coverage: All 39 correctness properties
- Integration test coverage: All API endpoints and UI workflows
- End-to-end test coverage: Complete user journeys (analyze → view → export)

### Testing Priorities

1. **Critical Path**: Workspace access → Analysis → Diagram generation → Rendering
2. **Security**: API key handling, data sanitization
3. **Error Handling**: All error scenarios produce appropriate responses
4. **Performance**: Large codebase handling, caching effectiveness
5. **Export**: All format exports produce valid outputs

## Implementation Notes

### Technology Stack Recommendations

**Frontend:**
- React or Vue.js for UI
- Mermaid.js for diagram rendering
- html2canvas + jsPDF for export
- WebSocket client for real-time updates

**Backend:**
- Node.js with Express or Python with FastAPI
- Anthropic SDK for Claude integration
- File system access libraries
- WebSocket server for progress updates

**Storage:**
- In-memory cache for analysis results
- Encrypted local storage for API keys
- Optional: Redis for distributed caching

### Security Considerations

1. **API Key Storage**: Use OS keychain or encrypted storage
2. **Input Sanitization**: Validate all file paths to prevent directory traversal
3. **Rate Limiting**: Implement client-side rate limiting for API calls
4. **CORS**: Configure appropriate CORS policies for web deployment
5. **Content Security**: Sanitize diagram code before rendering to prevent XSS

### Performance Optimizations

1. **Lazy Loading**: Load diagram renderers only when needed
2. **Code Splitting**: Split frontend bundle by route
3. **Worker Threads**: Use web workers for heavy processing
4. **Streaming**: Stream large file contents instead of loading entirely
5. **Debouncing**: Debounce user interactions to reduce re-renders

### Deployment Considerations

**Web Application:**
- Can be deployed as a static site with serverless functions
- Or as a full-stack application with Node.js/Python backend

**Desktop Application:**
- Can be packaged with Electron for native desktop experience
- Better file system access and performance

**VS Code Extension:**
- Alternative deployment as an IDE extension
- Direct workspace access without permission prompts
