#!/bin/bash
set -e

echo "[1/4] Checking tools..."
if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed."
    exit 1
fi

echo "[2/4] Building image..."
docker compose build --pull

echo "[3/4] Launching services..."
docker compose up -d

echo "[4/4] Verifying API status..."
# Wait for FastAPI to respond via internal check loop
for i in {1..12}; do
    if curl -fs http://localhost:8000/ > /dev/null 2>&1; then
        echo "API is healthy and online."
        break
    fi
    if [ $i -eq 12 ]; then
        echo "Warning: API startup timeout. Check logs."
    fi
    sleep 2
done

echo -e "\n=== Deployment Complete ==="
docker compose ps

echo -e "\nEndpoints available:"
echo "  API Health:  curl http://localhost:8000/"
echo "  Read Logs:   curl http://localhost:8000/api/logs"
echo "  pgAdmin UI:  http://<your_server_ip>:8080 (User: developer@local.dev / Pass: admin_pass)"
