# ms-expense-service

Servicio FastAPI encargado de **registrar, listar, actualizar y resumir** los gastos de cada usuario. Además expone un endpoint de carga masiva usado por el frontend para importar varios ítems a la vez.

## Características
- Modelo `Expense` con categorías (`ExpenseCategory`) y estado (`ExpenseStatus`).
- Normalización automática de etiquetas provenientes del frontend (`category_label`, `name`, `monto`, `cantidad`, etc.).
- Filtros por usuario, categoría y rango de fechas, además de resumen por categoría (`/expenses/summary/by-category`).
- Soporte para operaciones CRUD completas y para cargas masivas (`POST /expenses/bulk`).

## Migraciones
Los scripts SQL viven en `migrations/`. Cuando cambies el modelo sincroniza la base ejecutando:
```bash
mysql -u fintrack_admin -p fintrack_db < migrations/001_update_expenses_table.sql
```

## Ejecución
```bash
cd BackendFinTrack/ms-expense-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

Con Docker:
```bash
cd BackendFinTrack/ms-expense-service
docker compose up --build
```

## Endpoints principales
- `POST /expenses/`: crea un gasto individual. Acepta `category_label` para mapear etiquetas del frontend a `ExpenseCategory`.
- `POST /expenses/bulk`: recibe payloads tipo
  ```json
  {
    "user_id": 1,
    "category_label": "Servicios básicos",
    "items": [
      { "name": "Luz", "monto": 12000, "cantidad": 1 },
      { "name": "Internet", "monto": 18000, "cantidad": 1, "cuotas": 1 }
    ]
  }
  ```
  y los transforma en múltiples registros.
- `GET /expenses/`: filtra por `user_id`, `category`, `date_from`, `date_to`.
- `GET /expenses/{id}` / `PATCH /expenses/{id}` / `DELETE /expenses/{id}`: CRUD completo con control opcional por `user_id`.
- `GET /expenses/summary/by-category`: agrega los montos por categoría en un rango.

## Próximos pasos (testing sugerido)
La lógica del servicio vive en `app/services/expense_service.py`; recomendamos cubrirla con `pytest` + una base SQLite en memoria para validar `_prepare_amount_and_quantity`, cargas masivas y resúmenes. Actualmente no hay una suite incluida, por lo que cualquier aporte de pruebas será bienvenido.
