# 1) GET
curl "http://localhost:5000/number/?param=5"

# 2) POST
curl -X POST http://localhost:5000/number/ \
     -H "Content-Type: application/json" \
     -d '{"jsonParam":7}'

# 3) DELETE
curl -X DELETE http://localhost:5000/number/
