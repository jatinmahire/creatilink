# 🔧 MANUAL FIX - Change -a to -internal

## Your Current URL:
```
postgresql://creatilink_db_user:cuz9Bn985c0fVHnFPPHDX9ggFDBWewfu@dpg-d4fkdb4hg0os7392q0ig-a/creatilink_db
```

## ❌ Problem:
It ends with `-a` instead of `-internal`

## ✅ CORRECTED URL (Use This):
```
postgresql://creatilink_db_user:cuz9Bn985c0fVHnFPPHDX9ggFDBWewfu@dpg-d4fkdb4hg0os7392q0ig-internal/creatilink_db
```

**What changed:** `-a` → `-internal`

---

## 📋 EXACT STEPS:

### 1. Copy This Corrected URL:
```
postgresql://creatilink_db_user:cuz9Bn985c0fVHnFPPHDX9ggFDBWewfu@dpg-d4fkdb4hg0os7392q0ig-internal/creatilink_db
```

### 2. Update Environment Variable:
1. Go to your **Web Service** on Render
2. Click **"Environment"** tab
3. Find `DATABASE_URL`
4. Click **Edit** (pencil icon)
5. **Delete** the old URL
6. **Paste** the corrected URL above
7. Click **"Save Changes"**

### 3. Redeploy:
1. Click **"Manual Deploy"**
2. Select **"Clear build cache & deploy"**
3. Click **"Deploy"**
4. Wait 3-5 minutes

---

## 🎯 Remember:
- External URL: `dpg-XXXXX-a` ❌
- Internal URL: `dpg-XXXXX-internal` ✅

---

**Use the corrected URL above and redeploy!** 🚀
