from flask import Flask, request, jsonify, send_file
import json
import os
import tempfile
from generate_diagnosis import generate

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/generate', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        tmp.close()
        generate(data, tmp.name)
        return send_file(tmp.name, mimetype='application/pdf',
                        as_attachment=True,
                        download_name=f"diagnosis_{data.get('firstName','report')}.pdf")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
