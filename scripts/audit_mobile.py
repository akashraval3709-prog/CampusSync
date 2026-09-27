import os

missing_common_js = []
missing_viewport = []
all_templates = []

for root, dirs, files in os.walk(r'd:\Project_sem_5\A-project\CampusSync\templates'):
    for f in files:
        if f.endswith('.html') and not f.startswith('.'):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, r'd:\Project_sem_5\A-project\CampusSync\templates')
            all_templates.append(rel)
            txt = open(p, encoding='utf-8', errors='ignore').read()
            # If it's a full page (has <html or <body)
            if '<body' in txt or '<html' in txt:
                if 'common.js' not in txt:
                    missing_common_js.append(rel)
                if 'viewport' not in txt:
                    missing_viewport.append(rel)

print(f"Total HTML pages checked: {len(all_templates)}")
print(f"\nPages MISSING common.js (where sidebar button WILL NOT WORK!): {len(missing_common_js)}")
for p in missing_common_js:
    print("  -", p)

print(f"\nPages MISSING viewport meta tag (where mobile phone zoom/responsiveness breaks!): {len(missing_viewport)}")
for p in missing_viewport:
    print("  -", p)
