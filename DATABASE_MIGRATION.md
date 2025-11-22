# Database Migration Required

## New Columns Added to `projects` Table

The Drive Delivery System requires 3 new columns in the `projects` table.

### Migration SQL (Run on Render PostgreSQL)

```sql
-- Add delivery fields to projects table
ALTER TABLE projects ADD COLUMN IF NOT EXISTS delivery_link VARCHAR(500);
ALTER TABLE projects ADD COLUMN IF NOT EXISTS delivery_note TEXT;
ALTER TABLE projects ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP;
```

### How to Run on Render:

1. Go to https://dashboard.render.com
2. Select your PostgreSQL database
3. Click "Connect" → "External Connection"
4. Use the connection string to connect with a PostgreSQL client (like pgAdmin or psql)
5. Run the SQL commands above

### Alternative (via Python):

```python
# Run this in Python console or create a script
from app import db
db.session.execute('ALTER TABLE projects ADD COLUMN IF NOT EXISTS delivery_link VARCHAR(500)')
db.session.execute('ALTER TABLE projects ADD COLUMN IF NOT EXISTS delivery_note TEXT')
db.session.execute('ALTER TABLE projects ADD COLUMN IF NOT EXISTS delivered_at TIMESTAMP')
db.session.commit()
```

### Verify Migration:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'projects' 
AND column_name IN ('delivery_link', 'delivery_note', 'delivered_at');
```

You should see:
- delivery_link | character varying
- delivery_note | text
- delivered_at | timestamp without time zone

---

## Changes Made

### Backend:
- ✅ Added 3 columns to Project model
- ✅ Created `/projects/<id>/submit_delivery` route
- ✅ Validates Drive/Dropbox/OneDrive links

### Frontend:
- ✅ Creator Dashboard: Submit Delivery button + modal
- ✅ Customer Dashboard: Delivery link display
- ✅ Mark Complete only shows for 'delivered' status

### New Workflow:
```
open → assigned → [delivered] → completed
```

The new `delivered` status appears after creator submits Drive link.
