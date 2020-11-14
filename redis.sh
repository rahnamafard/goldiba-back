#!/usr/bin/env bash

set -euo pipefail

sudo docker run -d --name redis -v /var/lib/redis:/var/lib/redis redis:6.0.9
sudo docker run -d --name back -e REDIS_HOST=redis --link redis:redis -p 8081:8000 back
