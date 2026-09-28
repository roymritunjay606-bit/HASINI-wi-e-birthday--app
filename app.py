import os
import resend
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='.', static_url_path='')

RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
FROM_EMAIL     = os.environ.get('FROM_EMAIL', 'onboarding@resend.dev')
TO_EMAIL       = os.environ.get('TO_EMAIL', '')
SECRET_WORD    = os.environ.get('SECRET_WORD', '19082026')

resend.api_key = RESEND_API_KEY

def send_email(subject, body):
    if not (RESEND_API_KEY and TO_EMAIL):
        print('[email skipped] missing env vars')
        return False
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": TO_EMAIL,
            "subject": subject,
            "text": body
        })
        print('[email sent]', subject)
        return True
    except Exception as e:
        print('[email error]', e)
        return False

@app.route('/')
def index(): return send_from_directory('.', 'index.html')

@app.route('/api/unlock', methods=['POST'])
def unlock():
    data = request.get_json(silent=True) or {}
    pw = str(data.get('password', '')).strip()
    digits = ''.join(c for c in pw if c.isdigit())
    ok = digits == SECRET_WORD
    if ok: send_email("Unlocked", f"At {datetime.utcnow().isoformat()} UTC")
    return jsonify({'ok': ok}), 200

@app.route('/api/complete', methods=['POST'])
def complete():
    data = request.get_json(silent=True) or {}
    lines = ["OUR LITTLE WORLD — FINAL", "="*40,
             f"Time: {data.get('completed_at','')}",
             f"Choice: {data.get('choice','')}",
             f"No-attempts: {data.get('no_attempts',0)}", ""]
    for p in data.get('answers', []):
        lines.append(f"PAGE {p.get('page')}")
        for qa in p.get('answers', []):
            lines.append(f"Q: {qa.get('question','')}")
            lines.append(f"A: {qa.get('answer','')}")
        lines.append("")
    send_email("She finished Our Little World", "\n".join(lines))
    return jsonify({'ok': True}), 200

@app.route('/healthz')
def healthz(): return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
