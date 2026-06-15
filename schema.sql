-- Products table
CREATE TABLE products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT,
    sku         TEXT,
    currency    TEXT NOT NULL DEFAULT 'USD',
    is_active   BOOLEAN NOT NULL DEFAULT 1,
    deleted     BOOLEAN NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Unique only among rows that are not soft-deleted.
CREATE UNIQUE INDEX idx_products_sku ON products (sku) WHERE deleted = 0;
CREATE INDEX idx_products_is_active ON products (is_active);

-- Stock table (price and stock level per product)
CREATE TABLE stock (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL,
    price       NUMERIC(10, 2) NOT NULL DEFAULT 0,
    quantity    INTEGER NOT NULL DEFAULT 0,
    deleted     BOOLEAN NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE INDEX idx_stock_product_id ON stock (product_id);

-- Lookup table describing the different kinds of customer.
CREATE TABLE customer_type (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    name    TEXT NOT NULL,
    deleted BOOLEAN NOT NULL DEFAULT 0
);

-- Unique name only among rows that are not soft-deleted.
CREATE UNIQUE INDEX idx_customer_type_name ON customer_type (name) WHERE deleted = 0;

-- Customer table. Each customer references a row in customer_type.
CREATE TABLE customer (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    address          TEXT,
    customer_type_id INTEGER NOT NULL,
    deleted          BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (customer_type_id) REFERENCES customer_type (id)
);

CREATE INDEX idx_customer_customer_type_id ON customer (customer_type_id);

-- Product pricing: per-customer discount for a given product.
CREATE TABLE product_pricing (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    discount    NUMERIC(5, 2) NOT NULL DEFAULT 0,
    valid_from  DATE,
    valid_to    DATE,
    deleted     BOOLEAN NOT NULL DEFAULT 0,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES customer (id) ON DELETE CASCADE
);

-- One active discount per (product, customer, valid_from), ignoring soft-deleted rows.
CREATE UNIQUE INDEX idx_product_pricing_unique
    ON product_pricing (product_id, customer_id, valid_from) WHERE deleted = 0;
CREATE INDEX idx_product_pricing_product_id ON product_pricing (product_id);
CREATE INDEX idx_product_pricing_customer_id ON product_pricing (customer_id);
