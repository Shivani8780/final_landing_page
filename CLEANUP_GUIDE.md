# Files Safe to Remove for Railway Deployment

## Development Files (Can be removed):
- `add_test_item.py` (test script)
- `check_gallery.py` (verification script)
- `check_prod.py` (production check)
- `diagnose_db.py` (diagnostics)
- `init_db.py` (initialization script)
- `initialize_database.py` (duplicate init)
- `test_connection.py` (testing)
- `verify_db.py` (verification)
- `verify_gallery.py` (verification)

## Temporary/Backup Files:
- `query` (unknown temp file)
- `.git/COMMIT_EDITMSG` (git temp file)

## Deployment Files (Keep these):
- `main.py` (main app)
- `prod_config.py` (production config)
- `requirements.txt` (dependencies)
- `Procfile` (Railway config)
- `runtime.txt` (Python version)
- `railway-requirements.txt` (Railway deps)
- `render-requirements.txt` (Render deps)
- `migrations/` (database migrations)
- `templates/` (frontend files)
- `data/` (data files)

## Railway-Specific Recommendations:
1. Keep only one requirements file:
   - Delete either `railway-requirements.txt` or `render-requirements.txt`
2. Remove duplicate configs:
   - Keep either `render.yaml` or `railway-requirements.txt`

Note: Always test your deployment after removing files!
