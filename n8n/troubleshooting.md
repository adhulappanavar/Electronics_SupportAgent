# n8n LanceDB Connection Troubleshooting

## ✅ **FIXED: Connection ECONNREFUSED ::1:8000**

**Problem**: n8n was trying to connect to IPv6 localhost (`::1:8000`) instead of IPv4.

**Solution**: Updated workflow to use `http://127.0.0.1:8000/manual_search` instead of `http://localhost:8000/manual_search`.

---

## 🔧 **Quick Checks**

### 1. Verify LanceDB Service Status
```bash
cd /Users/anidhula/learn/lancedb/n8n
curl -s "http://127.0.0.1:8000/health"
```
**Expected**: `{"status":"healthy",...}`

### 2. Test Manual Search Endpoint
```bash
curl -s -X POST "http://127.0.0.1:8000/manual_search" \
     -H "Content-Type: application/json" \
     -d '{"question": "test"}'
```
**Expected**: Valid JSON response with `found`, `answer`, `confidence` fields

### 3. Check Service Process
```bash
lsof -ti:8000
```
**Expected**: Process ID number

---

## 🚀 **Start Services**

```bash
cd /Users/anidhula/learn/lancedb/n8n

# Start LanceDB service
python lance_code.py &

# Start Cognee service  
python congnee_code.py &

# Or use the automated startup
python start_services.py
```

---

## 🛑 **Common Issues & Fixes**

### Issue: Port Already in Use
```bash
# Kill existing processes
pkill -f lance_code.py
pkill -f congnee_code.py

# Wait and restart
sleep 2
python lance_code.py &
```

### Issue: Database Schema Error
```bash
# Remove old database and restart
rm -rf lancedb_data
python lance_code.py
```

### Issue: n8n Cannot Connect
- ✅ Use `127.0.0.1:8000` (not `localhost:8000`)
- Check firewall settings
- Ensure services are running
- Verify n8n can reach your machine

---

## 📋 **Service URLs**

- **LanceDB Health**: `http://127.0.0.1:8000/health`
- **LanceDB Manual Search**: `http://127.0.0.1:8000/manual_search`
- **Cognee Health**: `http://127.0.0.1:9000/health`
- **Cognee Query**: `http://127.0.0.1:9000/cognee_query` 