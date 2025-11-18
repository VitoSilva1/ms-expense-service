# ms-expense-service
Registrar, gestionar y categorizar los egresos.

## Migraciones manuales

Cuando cambies el esquema ejecuta primero los scripts en `migrations/`.  
Para alinear la tabla `expenses` con los modelos actuales:

```bash
mysql -u fintrack_admin -p Vicente5150. <basedatos> < migrations/001_update_expenses_table.sql
```
