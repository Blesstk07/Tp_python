# Gestion de stock - FastAPI

API de gestion de stock avec FastAPI, SQLAlchemy et MySQL. Les pages HTML sont
servies sous `/app` et l'API sous `/api`.

## Prerequis

- Python 3.11 ou plus recent
- MySQL 8.0.16 ou plus recent
- Le schema SQL commun et le fichier de donnees de test `seed.sql` fournis par
	le groupe

Sur la machine de developpement actuelle, MySQL 8.0.44 utilise le port `3307`
car MariaDB occupe le port `3306`.

## Installation

Depuis la racine du projet, dans PowerShell :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Creer le fichier local `.env` a partir de `.env.example`, puis renseigner le
mot de passe du compte MySQL `stock_user`. Ne jamais committer `.env`.

```dotenv
DB_URL=mysql+pymysql://stock_user:mot_de_passe@127.0.0.1:3307/gestion_stock_python?charset=utf8mb4
DB_POOL=10
```

Creer la base `gestion_stock_python` en `utf8mb4`, puis importer le schema et
le `seed.sql` communs dans cette base avant les tests d'integration.

## Lancement local

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8004 --reload
```

`--reload` est reserve au developpement.

## Lancement pour les mesures

Avant une mesure, restaurer la base depuis le `seed.sql` commun et arreter le
serveur de developpement. Lancer ensuite un seul worker, sans `--reload` et avec
une journalisation reduite :

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8004 --workers 1 --log-level warning
```

Conserver `DB_POOL=10` et ne lancer qu'une seule application a la fois. Les
scenarios k6, les niveaux de concurrence et les resultats sont a coordonner avec
le membre responsable des mesures.

- API : <http://127.0.0.1:8004>
- Verification : <http://127.0.0.1:8004/api/health>
- Documentation interactive : <http://127.0.0.1:8004/docs>
- Interface : <http://127.0.0.1:8004/app/>

## Tests

```powershell
python -m pytest -q
```

Les tests unitaires de validation et de montants ne necessitent pas MySQL. Les
tests d'integration et transactionnels necessitent le schema commun ainsi que
les donnees du `seed.sql` partage.

## Endpoints

- `GET /api/health`
- `GET|POST /api/products`, `GET|PUT|DELETE /api/products/{product_id}`
- `GET|POST /api/categories`, `PUT /api/categories/{category_id}`
- `GET|POST /api/suppliers`, `PUT /api/suppliers/{supplier_id}`
- `GET /api/stock`, `POST /api/stock/entries`, `GET /api/stock/movements`
- `GET|POST /api/sales`, `GET /api/sales/{sale_id}`
- `GET /api/dashboard`
