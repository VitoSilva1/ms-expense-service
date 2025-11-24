-- Actualiza la tabla expenses para que refleje el nuevo modelo/schemas
SET @schema := DATABASE();

-- Elimina notes si existe
SELECT IF(
    EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = @schema
          AND table_name = 'expenses'
          AND column_name = 'notes'
    ),
    'ALTER TABLE expenses DROP COLUMN notes;',
    'SELECT "notes ya fue eliminada";'
) INTO @drop_notes;
PREPARE stmt FROM @drop_notes;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Elimina currency si existe
SELECT IF(
    EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = @schema
          AND table_name = 'expenses'
          AND column_name = 'currency'
    ),
    'ALTER TABLE expenses DROP COLUMN currency;',
    'SELECT "currency ya fue eliminada";'
) INTO @drop_currency;
PREPARE stmt FROM @drop_currency;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agrega installments si todavía no existe
SELECT IF(
    EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = @schema
          AND table_name = 'expenses'
          AND column_name = 'installments'
    ),
    'SELECT "installments ya existe";',
    'ALTER TABLE expenses ADD COLUMN installments INT NULL AFTER amount;'
) INTO @add_installments;
PREPARE stmt FROM @add_installments;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Agrega quantity si todavía no existe
SELECT IF(
    EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = @schema
          AND table_name = 'expenses'
          AND column_name = 'quantity'
    ),
    'SELECT "quantity ya existe";',
    'ALTER TABLE expenses ADD COLUMN quantity INT NOT NULL DEFAULT 1 AFTER amount;'
) INTO @add_quantity;
PREPARE stmt FROM @add_quantity;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Asegura que category tenga los valores esperados por el modelo
ALTER TABLE expenses
    MODIFY COLUMN category ENUM(
        'service_basic',
        'supermarket',
        'credit_card',
        'bank_debts',
        'others'
    ) NOT NULL DEFAULT 'others';

-- Alinea el estado con los valores del enum ExpenseStatus
ALTER TABLE expenses
    MODIFY COLUMN status ENUM(
        'planned',
        'posted'
    ) NOT NULL DEFAULT 'posted';
