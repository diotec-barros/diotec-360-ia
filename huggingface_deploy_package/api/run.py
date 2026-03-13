#!/usr/bin/env python3
"""
Copyright 2024 Dionísio Sebastião Barros / DIOTEC 360

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Railway-compatible startup script
Reads PORT from environment variable correctly
"""
import os
import sys
from pathlib import Path

def main():
    # Add parent directory to Python path
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))
    
    # Get port from environment, default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting Aethel API on port {port}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path[0]}")
    
    # Import uvicorn
    import uvicorn
    
    # Run the app
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
