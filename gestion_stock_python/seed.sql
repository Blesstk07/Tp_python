
DROP TEMPORARY TABLE IF EXISTS _seed_numbers, _seed_sale_lines, _seed_supply_lines;

CREATE TEMPORARY TABLE _seed_numbers (
  n INT UNSIGNED NOT NULL PRIMARY KEY
);

INSERT INTO _seed_numbers (n)
SELECT ones.digit + 10 * tens.digit + 100 * hundreds.digit + 1
FROM (SELECT 0 AS digit UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS ones
CROSS JOIN (SELECT 0 AS digit UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS tens
CROSS JOIN (SELECT 0 AS digit UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) AS hundreds;

CREATE TEMPORARY TABLE _seed_sale_lines (
  line_no TINYINT UNSIGNED NOT NULL PRIMARY KEY
);
INSERT INTO _seed_sale_lines (line_no) VALUES (0), (1), (2), (3), (4);

CREATE TEMPORARY TABLE _seed_supply_lines (
  line_no TINYINT UNSIGNED NOT NULL PRIMARY KEY
);
INSERT INTO _seed_supply_lines (line_no) VALUES (0), (1), (2);

START TRANSACTION;

INSERT INTO categories (id, name, description)
SELECT n,
       CONCAT('Categorie ', LPAD(n, 2, '0')),
       CONCAT('Categorie de test ', LPAD(n, 2, '0'))
FROM _seed_numbers
WHERE n <= 20;

INSERT INTO suppliers (id, name, phone, email, address)
SELECT n,
       CONCAT('Fournisseur ', LPAD(n, 3, '0')),
       CONCAT('010000', LPAD(n, 4, '0')),
       CONCAT('fournisseur', LPAD(n, 3, '0'), '@example.test'),
       CONCAT('Adresse de test ', n)
FROM _seed_numbers
WHERE n <= 100;

INSERT INTO products (
  id, category_id, name, sku, description,
  purchase_price, sale_price, quantity, min_quantity
)
SELECT n,
       MOD(n - 1, 20) + 1,
       CONCAT('Produit ', LPAD(n, 4, '0')),
       CONCAT('SKU-', LPAD(n, 4, '0')),
       CONCAT('Produit de test ', LPAD(n, 4, '0')),
       50.00 + MOD(n, 50),
       100.00 + MOD(n, 100),
       5000,
       20
FROM _seed_numbers
WHERE n <= 1000;

INSERT INTO sales (id, reference, total_amount, created_at)
SELECT s.n,
       CONCAT('VTE-SEED-', LPAD(s.n, 4, '0')),
       SUM((1 + MOD(s.n + l.line_no, 3)) * p.sale_price),
       DATE_ADD('2026-01-01 00:00:00', INTERVAL s.n MINUTE)
FROM _seed_numbers AS s
CROSS JOIN _seed_sale_lines AS l
JOIN products AS p
  ON p.id = MOD((s.n - 1) * 5 + l.line_no, 1000) + 1
WHERE s.n <= 1000
GROUP BY s.n;

INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, subtotal)
SELECT s.n,
       p.id,
       1 + MOD(s.n + l.line_no, 3),
       p.sale_price,
       (1 + MOD(s.n + l.line_no, 3)) * p.sale_price
FROM _seed_numbers AS s
CROSS JOIN _seed_sale_lines AS l
JOIN products AS p
  ON p.id = MOD((s.n - 1) * 5 + l.line_no, 1000) + 1
WHERE s.n <= 1000;

INSERT INTO supplies (id, supplier_id, reference, total_amount, created_at)
SELECT s.n,
       MOD(s.n - 1, 100) + 1,
       CONCAT('APP-SEED-', LPAD(s.n, 4, '0')),
       SUM((10 + MOD(s.n + l.line_no, 5)) * p.purchase_price),
       DATE_ADD('2026-02-01 00:00:00', INTERVAL s.n MINUTE)
FROM _seed_numbers AS s
CROSS JOIN _seed_supply_lines AS l
JOIN products AS p
  ON p.id = MOD((s.n - 1) * 3 + l.line_no, 1000) + 1
WHERE s.n <= 200
GROUP BY s.n;

INSERT INTO supply_items (supply_id, product_id, quantity, unit_cost)
SELECT s.n,
       p.id,
       10 + MOD(s.n + l.line_no, 5),
       p.purchase_price
FROM _seed_numbers AS s
CROSS JOIN _seed_supply_lines AS l
JOIN products AS p
  ON p.id = MOD((s.n - 1) * 3 + l.line_no, 1000) + 1
WHERE s.n <= 200;

INSERT INTO stock_movements (
  product_id, movement_type, quantity, reference, note, created_at
)
SELECT si.product_id,
       'OUT',
       si.quantity,
       s.reference,
       'Mouvement de vente du jeu de test',
       s.created_at
FROM sale_items AS si
JOIN sales AS s ON s.id = si.sale_id;

INSERT INTO stock_movements (
  product_id, movement_type, quantity, reference, note, created_at
)
SELECT si.product_id,
       'IN',
       si.quantity,
       s.reference,
       'Mouvement d approvisionnement du jeu de test',
       s.created_at
FROM supply_items AS si
JOIN supplies AS s ON s.id = si.supply_id;

UPDATE products AS p
LEFT JOIN (
  SELECT product_id,
         SUM(CASE WHEN movement_type = 'IN' THEN quantity ELSE 0 END) AS qty_in,
         SUM(CASE WHEN movement_type = 'OUT' THEN quantity ELSE 0 END) AS qty_out
  FROM stock_movements
  GROUP BY product_id
) AS movements ON movements.product_id = p.id
SET p.quantity = 5000 + COALESCE(movements.qty_in, 0) - COALESCE(movements.qty_out, 0);

COMMIT;

DROP TEMPORARY TABLE IF EXISTS _seed_numbers, _seed_sale_lines, _seed_supply_lines;

-- Controle des volumes : attendu 20, 100, 1000, 1000, 5000, 200, 600, 5600.
SELECT
  (SELECT COUNT(*) FROM categories) AS categories,
  (SELECT COUNT(*) FROM suppliers) AS suppliers,
  (SELECT COUNT(*) FROM products) AS products,
  (SELECT COUNT(*) FROM sales) AS sales,
  (SELECT COUNT(*) FROM sale_items) AS sale_items,
  (SELECT COUNT(*) FROM supplies) AS supplies,
  (SELECT COUNT(*) FROM supply_items) AS supply_items,
  (SELECT COUNT(*) FROM stock_movements WHERE movement_type = 'OUT') AS movements_out,
  (SELECT COUNT(*) FROM stock_movements WHERE movement_type = 'IN') AS movements_in;

-- Ces deux controles doivent retourner 0 ligne.
SELECT s.id
FROM sales AS s
JOIN sale_items AS si ON si.sale_id = s.id
GROUP BY s.id, s.total_amount
HAVING s.total_amount <> SUM(si.subtotal);

SELECT s.id
FROM supplies AS s
JOIN supply_items AS si ON si.supply_id = s.id
JOIN products AS p ON p.id = si.product_id
GROUP BY s.id, s.total_amount
HAVING s.total_amount <> SUM(si.quantity * si.unit_cost);
