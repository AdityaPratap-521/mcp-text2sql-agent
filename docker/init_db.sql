-- Analytics PostgreSQL Enterprise Staging Database Initialization
CREATE TABLE IF NOT EXISTS regions (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    region_id INT REFERENCES regions(region_id),
    signup_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    stock_quantity INT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    total_amount NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    quantity INT NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL
);

-- Pre-populate Analytics Seed Data
INSERT INTO regions (region_name, country) VALUES
('North America', 'USA'),
('Europe', 'United Kingdom'),
('Asia Pacific', 'Japan'),
('Latin America', 'Brazil');

INSERT INTO customers (first_name, last_name, email, region_id, signup_date) VALUES
('Alice', 'Smith', 'alice.smith@cloudview.io', 1, '2024-01-15'),
('Bob', 'Jones', 'bob.jones@cloudview.io', 2, '2024-02-20'),
('Charlie', 'Brown', 'charlie.b@cloudview.io', 1, '2024-03-10'),
('David', 'Lee', 'david.lee@cloudview.io', 3, '2024-04-05'),
('Elena', 'Rostova', 'elena.r@cloudview.io', 2, '2024-05-12');

INSERT INTO products (product_name, category, unit_price, stock_quantity) VALUES
('Enterprise Cloud Suite', 'Software', 1200.00, 500),
('AI Analytics Server', 'Hardware', 4500.00, 50),
('Database Optimizer Tool', 'Software', 750.00, 200),
('Security Firewall Pro', 'Hardware', 2100.00, 80),
('Data Mesh Connector', 'Software', 950.00, 300);

INSERT INTO orders (customer_id, order_date, status, total_amount) VALUES
(1, '2025-07-10', 'COMPLETED', 5700.00),
(2, '2025-08-14', 'COMPLETED', 1200.00),
(3, '2025-08-28', 'COMPLETED', 2100.00),
(1, '2025-09-02', 'COMPLETED', 4500.00),
(4, '2025-09-15', 'COMPLETED', 5400.00),
(5, '2025-09-20', 'PENDING', 1900.00);

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 1200.00),
(1, 2, 1, 4500.00),
(2, 1, 1, 1200.00),
(3, 4, 1, 2100.00),
(4, 2, 1, 4500.00),
(5, 1, 2, 2400.00),
(5, 3, 4, 3000.00),
(6, 5, 2, 1900.00);
