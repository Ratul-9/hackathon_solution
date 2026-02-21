# BUILD COMMAND: docker build -t ratul9/blk-hacking-ind-ratul-mukherjee .
# Participant: Ratul Mukherjee

# OS: Debian-based Python image. Selected for robust C++ build tool support and stability.
FROM python:3.11-slim-bookworm

# Install C++ build dependencies + GIT (Required for FetchContent)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    && rm -rf /var/lib/apt-lists/*

WORKDIR /app

# Copy C++ source and CMake files
COPY CMakeLists.txt .
COPY engine/ ./engine/

# Build the C++ Engine
RUN mkdir build && cd build && \
    cmake .. && \
    cmake --build . --config Release 

# Copy Python requirements and source
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY api/ ./api/

# Requirement: Application must run on port 5477
EXPOSE 5477

# Run the FastAPI server
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "5477"]