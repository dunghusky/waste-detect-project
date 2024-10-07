### Install library
```sh
python3.11 -m venv venv
source venv/bin/activate  ## venv\Scripts\activate.bat
pip install -r requirements.txt

pip install 'uvicorn[standard]'

cp .env.examples .env  
```

### API
```bash
python3.11 app.py
```
