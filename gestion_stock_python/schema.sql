
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- idem : gestion_stock_java, gestion_stock_js, gestion_stock_python
 
CREATE TABLE categories (
  id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name        VARCHAR(100) NOT NULL,
  description VARCHAR(255) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
 
CREATE TABLE suppliers (
  id      BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name    VARCHAR(150) NOT NULL,
  phone   VARCHAR(30)  NULL,
  email   VARCHAR(150) NULL,
  address VARCHAR(255) NULL,
  PRIMARY KEY (id),
  KEY idx_suppliers_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
 
CREATE TABLE products (
  id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  category_id    BIGINT UNSIGNED NOT NULL,
  name           VARCHAR(150) NOT NULL,
  sku            VARCHAR(50)  NOT NULL,
  description    TEXT NULL,
  purchase_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  sale_price     DECIMAL(12,2) NOT NULL,
  quantity       INT NOT NULL DEFAULT 0,
  min_quantity   INT NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uq_products_sku (sku),
  KEY idx_products_name (name),
  KEY idx_products_category (category_id),
  CONSTRAINT fk_products_category FOREIGN KEY (category_id)
    REFERENCES categories (id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT ck_products_qty   CHECK (quantity >= 0),
  CONSTRAINT ck_products_minq  CHECK (min_quantity >= 0),
  CONSTRAINT ck_products_price CHECK (purchase_price >= 0 AND sale_price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
 
CREATE TABLE sales (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  reference    VARCHAR(50) NOT NULL,
  total_amount DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_sales_reference (reference),
  KEY idx_sales_created (created_at),
  CONSTRAINT ck_sales_total CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
 
CREATE TABLE sale_items (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  sale_id    BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  quantity   INT NOT NULL,
  unit_price DECIMAL(12,2) NOT NULL,
  subtotal   DECIMAL(14,2) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_sale_product (sale_id, product_id),
  KEY idx_sale_items_product (product_id),
  CONSTRAINT fk_si_sale    FOREIGN KEY (sale_id) REFERENCES sales (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_si_product FOREIGN KEY (product_id) REFERENCES products (id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT ck_si_qty CHECK (quantity > 0 AND unit_price >= 0 AND subtotal >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
 
CREATE TABLE supplies (
  id           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  supplier_id  BIGINT UNSIGNED NOT NULL,
  reference    VARCHAR(50) NOT NULL,
  total_amount DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_supplies_reference (reference),
  KEY idx_supplies_supplier (supplier_id),
  CONSTRAINT fk_supplies_supplier FOREIGN KEY (supplier_id)
    REFERENCES suppliers (id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT ck_supplies_total CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
 
CREATE TABLE supply_items (
  id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  supply_id  BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  quantity   INT NOT NULL,
  unit_cost  DECIMAL(12,2) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_supply_product (supply_id, product_id),
  KEY idx_supply_items_product (product_id),
  CONSTRAINT fk_spi_supply  FOREIGN KEY (supply_id) REFERENCES supplies (id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_spi_product FOREIGN KEY (product_id) REFERENCES products (id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT ck_spi_qty CHECK (quantity > 0 AND unit_cost >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
 
CREATE TABLE stock_movements (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  product_id    BIGINT UNSIGNED NOT NULL,
  movement_type VARCHAR(3) NOT NULL,          -- 'IN' ou 'OUT'
  quantity      INT NOT NULL,
  reference     VARCHAR(50) NOT NULL,         -- référence de la vente ou de l'appro
  note          VARCHAR(255) NULL,
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_mov_product_date (product_id, created_at),
  KEY idx_mov_reference (reference),
  CONSTRAINT fk_mov_product FOREIGN KEY (product_id)
    REFERENCES products (id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT ck_mov_type CHECK (movement_type IN ('IN','OUT')),
  CONSTRAINT ck_mov_qty  CHECK (quantity > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;