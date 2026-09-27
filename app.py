from flask import Flask, request, jsonify, send_from_directory
import os, smtplib
from email.message import EmailMessage
app=Flask(__name__, static_folder='../frontend', static_url_path='')

def send_email(subject, body):
    to=os.getenv('EMAIL_TO'); host=os.getenv('SMTP_HOST'); user=os.getenv('SMTP_USER'); pw=os.getenv('SMTP_PASS'); port=int(os.getenv('SMTP_PORT','587'))
    if not all([to,host,user,pw]): return False
    msg=EmailMessage(); msg['Subject']=subject; msg['From']=user; msg['To']=to; msg.set_content(body)
    with smtplib.SMTP(host,port) as s:
        s.starttls(); s.login(user,pw); s.send_message(msg)
    return True
@app.post('/api/submit')
def submit():
    data=request.get_json(silent=True) or {}; kind=data.get('type','unknown')
    if kind=='page_answers':
        body='Page %s answers:\n\n%s' % (data.get('page'), '\n\n'.join(f'{i+1}. {x}' for i,x in enumerate(data.get('answers',[]))))
        ok=send_email('What My Love Answered ❤️',body)
    elif kind=='final_choice':
        ok=send_email('Final answer from My Love ❤️',f"Final choice: {data.get('choice')}")
    else: return jsonify(ok=False),400
    return jsonify(ok=ok)
@app.get('/')
def index(): return send_from_directory('../frontend','index.html')
if __name__=='__main__': app.run(host='0.0.0.0',port=5000,debug=False)
