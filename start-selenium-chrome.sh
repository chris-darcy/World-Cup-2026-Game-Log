#!/usr/bin/env bash
set -e

docker run -d --name selenium-chrome -p 4444:4444 selenium/standalone-chrome:latest

echo "Selenium Chrome container started on http://localhost:4444"
