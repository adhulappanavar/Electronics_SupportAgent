# How to Activate the n8n Workflow

## Current Status
- ✅ n8n is running on http://127.0.0.1:5678
- ✅ LanceDB service is running on http://127.0.0.1:8000
- ❌ The "Simple LanceDB Test Workflow" is NOT ACTIVE

## Steps to Activate the Workflow

1. **Open n8n Web Interface**
   ```bash
   open http://127.0.0.1:5678
   ```

2. **Navigate to Workflows**
   - Click on "Workflows" in the left sidebar
   - Find "Simple LanceDB Test Workflow" (ID: LyK3qkZdvB841drn)

3. **Activate the Workflow**
   - Click on the workflow to open it
   - Look for the **toggle switch** in the top-right corner of the editor
   - **Turn it ON** to activate the workflow
   - The toggle should show as "Active" or have a green indicator

4. **Verify Activation**
   - Once activated, the webhook URL should be available
   - The webhook URL will be: `http://127.0.0.1:5678/webhook/test_lancedb`

## Test the Activated Workflow

After activation, you can test it with:

```bash
curl -X POST "http://127.0.0.1:5678/webhook/test_lancedb" \
  -H "Content-Type: application/json" \
  -d '{"query": "Samsung TV won'\''t turn on"}'
```

Or run the test script:
```bash
python test_correct_webhook.py
```

## Expected Response

When working correctly, you should get a response like:
```json
{
  "success": true,
  "query": "Samsung TV won't turn on",
  "lancedb_response": {
    "found": true,
    "confidence": 0.85,
    "answer": "Try unplugging the TV for 30 seconds...",
    "source_type": "manual_knowledge"
  },
  "timestamp": "2025-07-28T10:17:25.678613"
}
```

## Troubleshooting

- If the workflow doesn't activate, try refreshing the page
- Make sure you're logged into n8n
- Check that the workflow has no errors (red nodes)
- Verify that the LanceDB service is still running on port 8000 