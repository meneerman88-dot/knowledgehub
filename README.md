# Knowledge Hub Monitoring - CS3 Task 1

Dit project bevat de basis voor **Casestudy 3 - Task 1: Web Frontend Development**.

## Mapstructuur

```text
knowledgehub-monitoring/
│
├── api/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── requirements.txt
│   ├── seed_metrics.py
│   ├── logs/
│   └── .env
│
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env
│   ├── templates/
│   │   ├── login.html
│   │   └── dashboard.html
│   └── static/
│       └── style.css
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

## Start de API

```bash
cd api
pip install -r requirements.txt
python app.py
```

API draait op:

```text
http://localhost:8000
```

## Voeg testdata toe

Open een tweede terminal:

```bash
cd api
python seed_metrics.py
```

## Start de frontend

Open een derde terminal:

```bash
cd frontend
pip install -r requirements.txt
python app.py
```

Frontend draait op:

```text
http://localhost:5000
```

## Login

Klik op:

```text
Sign in with Entra ID
```

Dit is voor Task 1 nog een demo-login. In Task 2 wordt dit vervangen door echte Microsoft Entra ID OAuth/OIDC authenticatie.

## Wat is hiermee aangetoond voor Task 1?

- Er is een webinterface ontworpen op basis van het Figma frontend design.
- Er is een Flask frontend gemaakt met routes, templates en static assets.
- De frontend haalt monitoringdata op uit de bestaande CS2 API.
- De structuur is voorbereid voor Entra ID authenticatie in Task 2.
