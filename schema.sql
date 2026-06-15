-- Products table
CREATE TABLE products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT,
    sku         TEXT UNIQUE,
    currency    TEXT NOT NULL DEFAULT 'USD',
    is_active   BOOLEAN NOT NULL DEFAULT 1,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_sku ON products (sku);
CREATE INDEX idx_products_is_active ON products (is_active);

-- Stock table (price and stock level per product)
CREATE TABLE stock (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL,
    price       NUMERIC(10, 2) NOT NULL DEFAULT 0,
    quantity    INTEGER NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE INDEX idx_stock_product_id ON stock (product_id);

-- Lookup table describing the different kinds of customer.
CREATE TABLE customer_type (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Customer table. Each customer references a row in customer_type.
CREATE TABLE customer (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    address          TEXT,
    customer_type_id INTEGER NOT NULL,
    FOREIGN KEY (customer_type_id) REFERENCES customer_type (id)
);

CREATE INDEX idx_customer_customer_type_id ON customer (customer_type_id);
