import urllib.request
import uuid

def post_multipart(url, fields, files):
    boundary = uuid.uuid4().hex.encode('utf-8')
    CRLF = b'\r\n'
    data = []
    
    for key, value in fields.items():
        data.append(b'--' + boundary)
        data.append(f'Content-Disposition: form-data; name="{key}"'.encode('utf-8'))
        data.append(b'')
        data.append(str(value).encode('utf-8'))
        
    for key, (filename, content) in files.items():
        data.append(b'--' + boundary)
        data.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"'.encode('utf-8'))
        data.append(b'Content-Type: text/csv')
        data.append(b'')
        data.append(content.encode('utf-8'))
        
    data.append(b'--' + boundary + b'--')
    data.append(b'')
    
    body = CRLF.join(data)
    
    req = urllib.request.Request(url, data=body)
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary.decode("utf-8")}')
    req.add_header('Content-Length', str(len(body)))
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return f"Error: {e.code} - {e.read().decode('utf-8')}"

# Load test dataset
with open('test_dataset.csv', 'r') as f:
    csv_content = f.read()

url = 'http://127.0.0.1:8000/api/train/csv'
fields = {'text_column': 'text', 'label_column': 'label', 'test_size': '0.25'}
files = {'file': ('test_dataset.csv', csv_content)}

print(post_multipart(url, fields, files))
