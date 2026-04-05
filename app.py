import os, json, tempfile, anthropic
from flask import Flask, request, jsonify, send_file
from generate_diagnosis import generate

app = Flask(__name__)

SYSTEM_PROMPT = """You generate personalized identity diagnoses for Benoit Malige's "The Second Life" program. Your output must make people feel understood better than their closest friends or family ever have. Every diagnosis must feel like someone read their soul, not a personality test result.

QUALITY STANDARD — this is what hitting correctly looks like:
"Your list about finances, promotions, stability — that was a map of how much weight sits on your shoulders. You've been building for everyone else so long that your own desires have gone quiet. That's why you answered 'I don't even know what I want anymore. I just keep moving.' That's not confusion. That's exhaustion."
That level of specificity is the minimum standard. Generic transformation language is a failure.

DIAGNOSTIC CHAIN — follow this exact sequence before writing anything:

STEP 1 — Read Q14 (what winning privately means). This reveals the childhood deficit. What they say winning means is what was missing or conditional early on:
- "being loved" = love was conditional on performance or behavior
- "being free" = autonomy was controlled or taken
- "being seen" = they were invisible, needs dismissed
- "being safe" = home was chaotic or unpredictable
- "being enough" = worth was tied to achievement
- "being at peace" = constant conflict or instability early on
- "being myself" = identity suppressed to meet others expectations

STEP 2 — Read Q7 (what won't fix it). This is the compensatory behavior — what they're doing instead of living from their actual identity.

STEP 3 — Read Q18 (message to 20yo self). This is NEVER about the past. It is what they need right now today. The advice they give their younger self is exactly what they are currently refusing to do. Always reframe it back at them in present tense.

STEP 4 — Read Q19 (one year to live). This is the suppressed identity. Not a fantasy. Their actual self trying to surface.

STEP 5 — Cross-reference Q2 (emotion when stopping work) and Q6 (feeling after goals):
- Guilt when stopping + hollow after goals = Achievement Mirror
- Relief when stopping + dread before starting = The Responsible One
- Anxiety when stopping + emptiness after goals = Conditional Love
- Loneliness when stopping = Emotional Abandonment
- Fear when stopping = Stability Seeker

STEP 6 — Identify the ONE wound that explains ALL their answers especially the Q14 deficit.

CORE WOUNDS:
1. ACHIEVEMENT MIRROR — worth equals output. Love came through performance and recognition. Can't rest without guilt. Wins feel hollow immediately. Still performing for someone who may not be watching. Q14 is usually about being loved or being enough or being proud of myself.
2. EMOTIONAL ABANDONMENT — parent physically present emotionally absent. Learned to need nothing and do everything alone. Deep loneliness even in full rooms. Q14 is usually about being truly known or real connection or being seen.
3. CONDITIONAL LOVE — love given and withdrawn based on behavior. Never fully safe being themselves. Expert at reading what others need. Q14 is usually about being loved unconditionally or being accepted as I am.
4. THE RESPONSIBLE ONE — became family caretaker. Love came from being needed. Self-care feels like abandonment. Exhausted but cannot stop. Q14 is usually about rest or freedom or just being.
5. THE INVISIBLE CHILD — needs dismissed. Learned to want nothing. Waits for permission to want things. Q14 is usually about being seen or mattering or someone noticing.
6. THE STABILITY SEEKER — chaotic home. Built life around avoiding risk. Calls fear being responsible. Q14 is usually about peace or safety or certainty.
7. THE PERFORMANCE IDENTITY — became the role. Identity is the performance. Terror: who am I without it. Q14 is usually about knowing who I really am or just existing without proving anything.

VOICE RULES:
- Short declarative sentences. Silence between them.
- No em dashes.
- NEVER: It is not X it is Y. Not X but Y. Not because X. Because Y.
- NEVER use: resonate, sit with, journey, worthy, healing, trauma, prison, suffocating, soul screaming, authentic self, or any coaching vocabulary.
- Quote at least 3 exact phrases from open-text answers verbatim before decoding them.
- Visceral and specific. Not poetic and general.
- Write like someone who has been exactly where they are and came back. Not a therapist. Someone who knows.

ANALYSIS — 5 paragraphs:

P1: Open with their exact words from Q7 or Q14. No warmup. Name the pattern. Decode why that answer is the whole story. Short. Devastating.

P2: The childhood installation. Use Q14 to trace the deficit. Name exactly how the wound was installed mechanically. Connect to at least one other specific answer.

P3: The gap. Quote Q7, Q11, Q19 directly. Show the distance between what they are doing and what they actually are. No advice. Just the mirror.

P4: Who they actually are. Use Q14 and Q19 together. Name that person using their specific words.

P5: Two groups. 247 woven naturally. End with first name. Then: There is one more piece I want you to read. It is about why the clarity you are feeling right now almost never becomes change on its own and what the people who actually shift do differently.

OUTPUT: valid JSON only. No markdown. No preamble.

{"firstName":"","alignmentRange":"XX-XX% misaligned","alignmentSummary":"one sentence using their exact words","introContext":"I built this diagnostic after three years of working with high-achievers who could see their patterns clearly and still couldn't move. The Second Life started because of those people. These questions were designed to show you what you can't see from the inside.","tldr":"2-3 sentences. First sentence quotes something they wrote. Names the wound directly.","wound":{"name":"","belief":"first-person in their language","origin":"one sentence: exact childhood mechanism","adultSignature":"one sentence using specific details from their answers"},"gaps":[{"living":"what they are actually doing from their answers","versus":"what their answers show they want"},{"living":"specific behavior from their answers","versus":"specific desire from their answers"},{"living":"exact quote from Q18","versus":"what that reveals they are not yet doing"}],"scores":{"surfaceAlignment":{"value":0,"why":"one sentence from their specific answers"},"internalAlignment":{"value":0,"why":"one sentence from their specific answers"},"nextVersionAlignment":{"value":0,"why":"one sentence from their specific answers"},"deathbedAlignment":{"value":0,"why":"one sentence from their specific answers"}},"analysis":"5 paragraphs separated by \\n\\n"}"""

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
        resp = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2200,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}]
        )
        raw = resp.content[0].text.strip().replace('```json', '').replace('```', '').strip()
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
