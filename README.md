# FastAPI loan amortization app

### Suggested usage (local development only)

1. Create virtual environment and install requirements, e.g.
```commandline
python -m venv env
source ./env/activate
pip install -r requirements.txt
```


2. Run tests:
```commandline
pytest -v
```


3. Start the development server:
>   **Note:** For Windows users I recommend doing this from Powershell (some exception happens when I try from Git Bash).
```commandline
fastapi dev ./app/main.py
```


4. Navigate to the [Swagger UI](http://127.0.0.1:8000/docs).
   The admin username / password is `admin` / `ok`.
