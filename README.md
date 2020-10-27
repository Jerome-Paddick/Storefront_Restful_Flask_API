To RUN:

1. docker volume create postgres_database
1. docker-compose up -d
2. docker exec -it api sh
3. cd app
4. flask db upgrade
5. flask populate-db
5. Head over to -> http://localhost:5000/api/api_documentation.html
6. Enter Timestamp into api endpoint

 ---
 Tests
 
 - (after docker image is live and db populated)
 1. docker exec -it api sh
 2. pytest
 
---
Improvements

Obviously this is pretty barebones by design, but it could have:
 - Authentication 
 - A central logging system instead of returning errors from api endpoints, 
 - A reverse Proxy such as NGINX
 - auto-scaling, high availability, and a custom url on AWS for example
 - more tests
 
