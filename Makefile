PYTHON ?= python
PIP ?= pip

.PHONY: install install-full test demo api dashboard ingest evaluate monitor docker-up docker-down

install:
	$(PIP) install -r requirements-minimal.txt

install-full:
	$(PIP) install -r requirements.txt

test:
	PYTHONPATH=src pytest

demo:
	PYTHONPATH=src $(PYTHON) scripts/run_demo.py

api:
	PYTHONPATH=src uvicorn safetyreview_ai.api.main:app --reload

dashboard:
	PYTHONPATH=src streamlit run dashboards/streamlit_app.py

ingest:
	PYTHONPATH=src $(PYTHON) scripts/ingest_knowledge_base.py

evaluate:
	PYTHONPATH=src $(PYTHON) scripts/evaluate_system.py

monitor:
	PYTHONPATH=src $(PYTHON) scripts/monitor_system.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down
