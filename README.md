# BlackRock Auto-Save & Investment Engine

A high-performance, hybrid Python-C++ system designed to process large-scale financial transactions (up to $10^6$ constraints) using an optimized **Sweep-line Algorithm**. This engine automates rounding-based savings, validates them against complex financial and temporal rules, and calculates real-world returns for NPS and Index Fund portfolios.

## 🚀 System Architecture

The project utilizes a **Polyglot Architecture** to balance developer productivity with computational performance:
* **FastAPI Orchestrator (Python):** Handles the web interface, Pydantic data validation, and multi-stage financial filtering.
* **Core Logic Engine (C++):** A high-performance backend that executes the sweep-line algorithm for $O((N+Q+P) \log (N+Q+P))$ time complexity.



---

## 📂 Project Structure

```text
root/
├── api/
│   └── main.py          # FastAPI Orchestrator & Multi-stage APIs
├── engine/
│   └── main.cpp         # C++ Sweep-line Core Logic
├── build/               # Generated upon C++ compilation (git ignored)
├── venv/                # Python virtual environment (git ignored)
├── CMakeLists.txt       # C++ Build Configuration
├── compose.yaml         # Docker Compose multi-service configuration
├── Dockerfile           # Docker image definition for backend
├── requirements.txt     # Python dependencies list
└── README.md            # Project documentation

⚙️ Local Setup & Installation
-----------------------------

Follow these steps to set up the development environment on your local machine.

### 1\. Build the C++ Engine

Ensure you have a C++ compiler (MSVC, MinGW, or GCC) and CMake installed.

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # Create build directory and navigate into it  mkdir build  cd build  # Generate build files and compile the engine  # This will also fetch nlohmann/json automatically via FetchContent  cmake ..  cmake --build . --config Release  # Return to root directory  cd ..   `

### 2\. Set Up Python Virtual Environment

Requires Python 3.11 or higher.

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # Create the virtual environment  python -m venv venv  # Activate the virtual environment  # On Windows:  .\venv\Scripts\activate  # On macOS/Linux:  source venv/bin/activate  # Install the required dependencies  pip install -r requirements.txt   `

### 3\. Run the Development Server

Launch the FastAPI server using Uvicorn.

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python -m uvicorn api.main:app --reload   `

The server will be live at http://127.0.0.1:8000.

🐳 Docker Deployment
--------------------

The application is fully containerized to meet hackathon requirements.

### Build and Run

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # Build the image as per participant requirements  docker build -t ratul9/blk-hacking-ind-ratul-mukherjee .  # Run the container with the required port mapping  docker run -d -p 5477:5477 ratul9/blk-hacking-ind-ratul-mukherjee   `

### Docker Compose

To run using the provided compose.yaml:

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   docker-compose up -d --build   `

📡 API Reference
----------------

### i) Transaction Builder (/transactions:parse)

*   **Method:** POST
    
*   **Goal:** Rounds amount to nearest 100 ceiling and calculates remanent.
    
*   **Sample Body:**
    

JSON

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   [    { "date": "2023-02-28 15:49:20", "amount": 375 }  ]   `

### ii) Financial Validator (/transactions:validator)

*   **Method:** POST
    
*   **Goal:** Validates remanents against wage limits (10% cap or ₹2L max).
    
*   **Sample Body:**
    

JSON

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   {    "wage": 50000,    "transactions": [      { "id": "txn_0", "date": "2023-02-28 15:49:20", "amount": 375, "ceiling": 400, "remanent": 25, "status": "valid" }    ]  }   `

### iii) Temporal Filter (/transactions:filter)

*   **Method:** POST
    
*   **Goal:** Validates date formats and year constraints for $k$-periods.
    
*   **Sample Body:**
    

JSON

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   {    "wage": 50000,    "q_periods": [{ "start": "2023-07-01 00:00:00", "end": "2023-07-31 23:59:59", "fixed": 0 }],    "transactions": [...]  }   `

### iv) Composite Orchestrators (/returns:nps & /returns:index)

*   **Method:** POST
    
*   **Goal:** Executes full pipeline and triggers the C++ Sweep-line engine.
    
*   **Sample Body:**
    

JSON

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   {    "age": 29,    "wage": 50000,    "inflation": 5.5,    "q": [], "p": [], "k": [],    "transactions": []  }   `

### v) Performance Report (/performance-report)

*   **Method:** GET
    
*   **Output:** Returns JSON telemetry containing peakMB memory usage and totalEngineCalls.
    

👤 Author
---------

**Ratul Mukherjee** Student at **Institute of Engineering and Management (IEM), Kolkata** B.Tech in Computer Science and Business Systems