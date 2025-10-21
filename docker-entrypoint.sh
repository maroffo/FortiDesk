#!/bin/bash
set -e

echo "Waiting for database to be ready..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if python -c "import pymysql; pymysql.connect(host='db', user='${MYSQL_USER:-fortidesk}', password='${MYSQL_PASSWORD:-fortidesk123}', database='${MYSQL_DATABASE:-fortidesk}')" 2>/dev/null; then
        echo "Database is ready!"
        break
    fi
    retry_count=$((retry_count + 1))
    echo "Database not ready yet (attempt $retry_count/$max_retries)..."
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "Failed to connect to database after $max_retries attempts"
    exit 1
fi

echo "Initializing database tables and default users..."
python << END
from run import init_db

# Call the init_db function which creates tables and default users
init_db()
END

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 run:app
