# ms-expense-service
Registrar, gestionar y categorizar los egresos.

## Migraciones manuales

Cuando cambies el esquema ejecuta primero los scripts en `migrations/`.  
Para alinear la tabla `expenses` con los modelos actuales:

```bash
mysql -u fintrack_admin -p Vicente5150. <basedatos> < migrations/001_update_expenses_table.sql
```

## Endpoints clave

- `POST /expenses/`: crea un gasto individual. Soporta los campos clásicos (`description`, `amount`, `quantity`, `installments`, etc.) y opcionalmente `category_label` para mapear etiquetas del frontend (`"Servicios básicos"`, `"Supermercado"`, etc.).
- `POST /expenses/bulk`: pensado para la vista de Frontend (`Expenses.jsx`). Permite enviar múltiples filas en un solo request:

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

Los campos `name`, `monto`, `cantidad` y `cuotas` se aceptan tal como los genera el frontend; internamente se normalizan a `description`, `amount`, `quantity` e `installments`.
