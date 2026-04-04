import os, json, tempfile, anthropic
from flask import Flask, request, jsonify, send_file
from generate_diagnosis import generate

app = Flask(__name__)

SYSTEM_PROMPT = """You generate personalized identity diagnoses for Benoit Malige's "The Second Life" program. Output valid JSON only. No markdown fences, no preamble.

VOICE: Short declarative sentences. No em dashes. No "not X but Y". No therapy vocab. Mirror their exact words. Visceral and specific.

WOUND - pick ONE: ACHIEVEMENT MIRROR, EMOTIONAL ABANDONMENT, CONDITIONAL LOVE, THE RESPONSIBLE ONE, THE INVISIBLE CHILD, THE STABILITY SEEKER, THE PERFORMANCE IDENTITY.

MISALIGNMENT RANGE: never above 75%.

OUTPUT FORMAT - fill every field with real analysis based on the answers:
{"firstName":"","alignmentRange":"","alignmentSummary":"","introContext":"I built this diagnostic after three years of working with high-achievers who could see their patterns clearly and still couldn't move. The Second Life started because of those people. These questions were designed to show you what you can't see from the inside.","tldr":"","wound":{"name":"","belief":"","origin":"","adultSignature":""},"gaps":[{"living":"","versus":""},{"living":"","versus":""},{"living":"","versus":""}],"scores":{"surfaceAlignment":{"value":0,"why":""},"internalAlignment":{"value":0,"why":""},"nextVersionAlignment":{"value":0,"why":""},"deathbedAlignment":{"value":0,"why":""}},"analysis":"5 paragraphs separated by two newlines"}"""

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/tally', methods=['POST'])
def tally_webhook():
    try:
        data = request.get_json(force=True)
        fields = data.get('data', {}).get('fields', data.get('fields', {}))
        lines = []
        if isinstance(fields, dict):
            for k, v in fields.items():
                if isinstance(v, list):
                    v = v[0] if len(v) == 1 else ', '.join(str(x) for x in v)
                lines.append(f"{k}: {v}")
        user_msg = '\n'.join(lines)
        client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
        resp = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=2200, system=SYSTEM_PROMPT, messages=[{"role":"user","content":user_msg}])
        raw = resp.content[0].text.strip().replace('```json','').replace('```','').strip()
        diagnosis = json.loads(raw)
        tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        tmp.close()
        generate(diagnosis, tmp.name)
        return send_file(tmp.name, mimetype='application/pdf', as_attachment=True, download_name=f"diagnosis_{diagnosis.get('firstName','report')}.pdf")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_pdf():
    try:
        data = request.get_json()
        tmp = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        tmp.close()
        generate(data, tmp.name)
        return send_file(tmp.name, mimetype='application/pdf', as_attachment=True, download_name=f"diagnosis_{data.get('firstName','report')}.pdf")
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
