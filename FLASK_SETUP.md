# Flask + Jinja2 Template Setup

## 🎯 What Changed

Your application is now built with **Flask + Jinja2 + HTML/CSS** instead of Gradio. This gives you complete control over the UI/UX!

## 📁 Project Structure

```
dialogue-episode-annotator/
├── app.py                    # Flask app (main entry point)
├── requirements.txt          # Updated with Flask + python-dotenv
├── templates/                # HTML templates (edit these!)
│   ├── index.html           # Main page
│   ├── 404.html             # 404 error page
│   └── 500.html             # 500 error page
├── static/                   # Static files (CSS/JS/images)
│   ├── css/
│   │   └── style.css        # Stylesheet (customize here!)
│   └── js/
│       └── app.js           # Frontend JavaScript (edit this!)
└── app/                      # Core modules (unchanged)
    ├── analytics.py
    ├── summarizer.py
    └── ...
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Locally
```bash
python app.py
```

Then open: http://localhost:7860

### 3. Edit HTML/CSS

- **HTML**: Edit `templates/index.html` to change the layout
- **CSS**: Edit `static/css/style.css` to change styling
- **JavaScript**: Edit `static/js/app.js` for interactivity

## 📝 Editing Guide

### HTML (templates/index.html)
Add sections, change form fields, reorganize layouts:

```html
<section class="my-section">
    <h2>Your Heading</h2>
    <p>Your content</p>
</section>
```

### CSS (static/css/style.css)
Customize colors, sizes, spacing, responsive behavior:

```css
.my-section {
    background-color: #f0f4f8;
    padding: 2rem;
    border-radius: 8px;
}
```

### JavaScript (static/js/app.js)
Add interactivity, handle events, fetch data:

```javascript
document.getElementById('my-btn').addEventListener('click', () => {
    console.log('Button clicked!');
});
```

## 🎨 Customization Examples

### Change Colors
Edit `:root` variables in `static/css/style.css`:

```css
:root {
    --primary-color: #2563eb;      /* Change this */
    --secondary-color: #64748b;    /* Or this */
}
```

### Add New Form Fields
Edit `templates/index.html`:

```html
<div class="form-group">
    <label for="my-field">My Field</label>
    <input type="text" id="my-field" name="my_field">
</div>
```

### Add New API Endpoint
Edit `app.py`:

```python
@app.route('/api/my-endpoint', methods=['POST'])
def my_endpoint():
    data = request.get_json()
    # Do something
    return jsonify({'result': 'success'})
```

## 📱 Responsive Design

The layout is mobile-friendly using CSS Grid/Flexbox. Adjust breakpoints in `static/css/style.css`:

```css
@media (max-width: 768px) {
    .upload-section {
        grid-template-columns: 1fr;  /* Stack on mobile */
    }
}
```

## 🔧 API Endpoints

### POST /api/upload
Upload a CSV file
```javascript
const formData = new FormData();
formData.append('file', file);
const res = await fetch('/api/upload', { method: 'POST', body: formData });
```

### POST /api/process/<session_id>
Process uploaded file
```javascript
const res = await fetch(`/api/process/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ enable_summary: true, max_words: 150 })
});
```

### GET /api/download/<session_id>
Download results as CSV

## 🚀 Deploy to HF Spaces

The Flask app is ready to deploy! Just push to HF:

```bash
git add -A
git commit -m "feat: Convert to Flask + Jinja2 with custom HTML/CSS"
git push origin master
```

HF Spaces will auto-detect Flask and deploy it.

## 🎯 Tips

1. **Reload on save**: Use a dev server with hot reload:
   ```bash
   pip install flask-reload
   ```

2. **Browser DevTools**: Use F12 to inspect/debug HTML/CSS/JS

3. **Console logging**: Check browser console for JavaScript errors

4. **Network tab**: Check API calls and responses in Network tab

## 📚 File-by-File Guide

### app.py
- Main Flask app
- API endpoints: /api/upload, /api/process, /api/download
- Error handlers

### templates/index.html
- Main page layout
- Form inputs
- Results display
- Help section

### static/css/style.css
- Global styles & colors
- Component styles
- Responsive breakpoints
- Dark mode ready

### static/js/app.js
- File upload handling
- Form submission
- Tab switching
- Download functionality
- Status messages

## 🤝 Need Help?

Check these sections:
- **HTML Layout**: templates/index.html
- **Styling**: static/css/style.css  
- **Behavior**: static/js/app.js
- **Backend**: app.py

Good luck! 🚀
