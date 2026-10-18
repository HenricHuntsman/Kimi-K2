#!/usr/bin/env python3
"""Demonstration UI with an explicit opt-in local Ollama chat backend."""

from flask import Flask, render_template, request, jsonify, send_from_directory
from forge_implementation import ForgeAI
from forge_local import LocalOllama, LocalModelError
import os
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 256 * 1024
forge = None


def configured_backend():
    backend = os.environ.get('FORGE_BACKEND', 'demo')
    if backend not in ('demo', 'ollama'):
        raise LocalModelError('FORGE_BACKEND must be demo or ollama')
    return backend

# Initialize THE FORGE
def init_forge():
    global forge
    if forge is None:
        forge = ForgeAI()
        forge.initialize()
        print("✅ THE FORGE GUI initialized successfully!")

@app.route('/')
def index():
    """Main GUI interface"""
    return render_template('index.html')

@app.route('/api/init', methods=['GET'])
def api_init():
    """Initialize THE FORGE and return stats"""
    init_forge()
    try:
        backend = configured_backend()
        model = LocalOllama.from_environment().model if backend == 'ollama' else None
    except LocalModelError as error:
        return jsonify({'error': str(error)}), 503
    
    stats = {
        'total_capabilities': 0,
        'documents_loaded': len(forge.loader.documents),
        'total_characters': sum(len(content) for content in forge.loader.documents.values()),
        'categories': [],
        'status': 'demonstration' if backend == 'demo' else 'local_model_configured',
        'backend': backend,
        'model': model,
        'inference_verified': False,
        'model_loaded': False if backend == 'demo' else None,
        'version': '1.0.0',
        'name': 'FORGE Local Chat Lab'
    }
    
    return jsonify(stats)

@app.route('/api/capabilities', methods=['GET'])
def api_capabilities():
    """Get all capabilities organized by category"""
    init_forge()
    
    return jsonify({})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat interface"""
    init_forge()
    
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('message'), str):
        return jsonify({'error': 'message must be a string'}), 400
    message = data['message']
    if not message.strip():
        return jsonify({'error': 'message must not be empty'}), 400
    mode = data.get('mode', 'chat')
    if not isinstance(mode, str):
        return jsonify({'error': 'mode must be a string'}), 400
    try:
        backend = configured_backend()
        if backend == 'ollama':
            response = LocalOllama.from_environment().chat([{'role': 'user', 'content': message}])
            response.update(mode=mode, timestamp=datetime.now().isoformat())
            return jsonify(response)
    except LocalModelError as error:
        return jsonify({'error': str(error), 'backend': 'ollama',
                        'inference_verified': False, 'capabilities_used': []}), 503
    
    # Generate response based on mode
    response = {
        'message': f"[DEMO — no model loaded] Echo: {message}",
        'mode': mode,
        'timestamp': datetime.now().isoformat(),
        'demo': True,
        'model_loaded': False,
        'capabilities_used': []
    }
    
    return jsonify(response)

@app.route('/api/tools/<tool_name>', methods=['POST'])
def api_tool(tool_name):
    """Execute specific tool"""
    init_forge()
    
    known_tools = {'code-review', 'book-analyze', 'image-upscale', 'video-edit'}
    known = tool_name in known_tools
    return jsonify({
        'name': tool_name.replace('-', ' ').title(),
        'status': 'not_implemented' if known else 'unknown_tool',
        'executed': False,
        'demo': True,
        'result': 'No tool executed. This interface is a demonstration.'
    }), 501 if known else 404

@app.route('/api/skills', methods=['GET'])
def api_skills():
    """Get all skills with statistics"""
    init_forge()
    
    return jsonify({'total': 0, 'demo': True, 'implemented': False})

@app.route('/api/documentation/<path:doc_name>', methods=['GET'])
def api_documentation(doc_name):
    """Get specific documentation"""
    init_forge()
    
    if doc_name in forge.loader.documents:
        doc = forge.loader.documents[doc_name]
        return jsonify({
            'name': doc_name,
            'content': doc,
            'size': len(doc),
            'capabilities': 0,
            'historical_documentation': True,
            'preview': doc[:500] + '...'
        })
    
    return jsonify({'error': 'Document not found'}), 404

@app.route('/static/<path:path>')
def send_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

if __name__ == '__main__':
    # Create static and templates directories
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/icons', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("🔥 Starting THE FORGE GUI...")
    print("📍 Open http://localhost:5000 in your browser")
    print("Backend: " + os.environ.get('FORGE_BACKEND', 'demo') + "; no tools execute.")
    
    app.run(debug=False, host='127.0.0.1', port=5000)
