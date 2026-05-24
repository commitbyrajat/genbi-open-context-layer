DROP TABLE IF EXISTS employee_projects;
DROP TABLE IF EXISTS performance_reviews;
DROP TABLE IF EXISTS salaries;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
    department_id BIGSERIAL PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    business_unit VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    employee_id BIGSERIAL PRIMARY KEY,
    employee_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    department_id BIGINT NOT NULL REFERENCES departments(department_id),
    manager_id BIGINT REFERENCES employees(employee_id),
    job_level VARCHAR(30) NOT NULL,
    hire_date DATE NOT NULL,
    employment_status VARCHAR(30) NOT NULL
);

CREATE TABLE projects (
    project_id BIGSERIAL PRIMARY KEY,
    project_name VARCHAR(150) NOT NULL,
    project_type VARCHAR(80) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    budget NUMERIC(14,2) NOT NULL,
    project_status VARCHAR(30) NOT NULL
);

CREATE TABLE employee_projects (
    employee_project_id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL REFERENCES employees(employee_id),
    project_id BIGINT NOT NULL REFERENCES projects(project_id),
    allocation_percent NUMERIC(5,2) NOT NULL,
    role_on_project VARCHAR(80) NOT NULL,
    billable BOOLEAN NOT NULL,
    UNIQUE(employee_id, project_id)
);

CREATE TABLE performance_reviews (
    review_id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL REFERENCES employees(employee_id),
    review_period VARCHAR(20) NOT NULL,
    performance_score NUMERIC(4,2) NOT NULL,
    potential_rating VARCHAR(30) NOT NULL,
    promotion_recommended BOOLEAN NOT NULL,
    attrition_risk VARCHAR(20) NOT NULL
);

CREATE TABLE salaries (
    salary_id BIGSERIAL PRIMARY KEY,
    employee_id BIGINT NOT NULL REFERENCES employees(employee_id),
    effective_from DATE NOT NULL,
    annual_salary NUMERIC(14,2) NOT NULL,
    currency VARCHAR(10) NOT NULL
);

INSERT INTO departments (department_name, business_unit, location) VALUES
('Engineering', 'Technology', 'Bengaluru'),
('Data Platform', 'Technology', 'Hyderabad'),
('Product Management', 'Digital', 'Mumbai'),
('Information Security', 'Risk', 'Pune'),
('Operations', 'Shared Services', 'Delhi');

INSERT INTO employees (employee_name, email, department_id, manager_id, job_level, hire_date, employment_status) VALUES
('Amit Sharma', 'amit.sharma@example.com', 1, NULL, 'L6', '2018-04-10', 'active'),
('Neha Rao', 'neha.rao@example.com', 2, NULL, 'L6', '2017-09-15', 'active'),
('Rajat Mehta', 'rajat.mehta@example.com', 1, 1, 'L4', '2021-01-20', 'active'),
('Sara Khan', 'sara.khan@example.com', 1, 1, 'L3', '2022-06-01', 'active'),
('Vikram Nair', 'vikram.nair@example.com', 2, 2, 'L4', '2020-11-12', 'active'),
('Priya Iyer', 'priya.iyer@example.com', 3, NULL, 'L5', '2019-02-18', 'active'),
('Karan Verma', 'karan.verma@example.com', 4, NULL, 'L5', '2019-08-25', 'active'),
('Meera Joshi', 'meera.joshi@example.com', 5, NULL, 'L5', '2016-12-05', 'active'),
('Ananya Das', 'ananya.das@example.com', 3, 6, 'L3', '2023-01-10', 'active'),
('Rohan Gupta', 'rohan.gupta@example.com', 5, 8, 'L2', '2023-04-14', 'active');

INSERT INTO projects (project_name, project_type, start_date, end_date, budget, project_status) VALUES
('Core Banking Modernization', 'Transformation', '2024-01-01', '2024-12-31', 25000000, 'active'),
('GenBI Semantic Layer', 'AI Analytics', '2024-03-01', NULL, 12000000, 'active'),
('Zero Trust Security Rollout', 'Security', '2024-02-15', '2024-11-30', 9000000, 'active'),
('Employee Self Service Portal', 'Digital Experience', '2024-04-01', NULL, 7000000, 'active'),
('Legacy Ops Automation', 'Automation', '2024-01-15', '2024-09-30', 5000000, 'completed');

INSERT INTO employee_projects (employee_id, project_id, allocation_percent, role_on_project, billable) VALUES
(1, 1, 40, 'Solution Architect', true),
(1, 2, 30, 'Architecture Reviewer', true),
(2, 2, 60, 'Data Platform Lead', true),
(3, 1, 80, 'Backend Engineer', true),
(3, 2, 20, 'Semantic Model Engineer', true),
(4, 4, 70, 'Frontend Engineer', true),
(5, 2, 90, 'Data Engineer', true),
(6, 4, 60, 'Product Owner', false),
(7, 3, 80, 'Security Architect', true),
(8, 5, 70, 'Operations Lead', false),
(9, 4, 80, 'Business Analyst', false),
(10, 5, 90, 'Ops Analyst', false);

INSERT INTO performance_reviews (employee_id, review_period, performance_score, potential_rating, promotion_recommended, attrition_risk) VALUES
(1, '2024-H1', 4.60, 'high', true, 'low'),
(2, '2024-H1', 4.40, 'high', true, 'medium'),
(3, '2024-H1', 4.20, 'high', true, 'medium'),
(4, '2024-H1', 3.50, 'medium', false, 'medium'),
(5, '2024-H1', 4.70, 'high', true, 'high'),
(6, '2024-H1', 4.10, 'medium', false, 'low'),
(7, '2024-H1', 4.30, 'high', true, 'low'),
(8, '2024-H1', 3.80, 'medium', false, 'medium'),
(9, '2024-H1', 3.60, 'medium', false, 'high'),
(10, '2024-H1', 3.20, 'low', false, 'high');

INSERT INTO salaries (employee_id, effective_from, annual_salary, currency) VALUES
(1, '2024-04-01', 5200000, 'INR'),
(2, '2024-04-01', 5000000, 'INR'),
(3, '2024-04-01', 2800000, 'INR'),
(4, '2024-04-01', 1800000, 'INR'),
(5, '2024-04-01', 3000000, 'INR'),
(6, '2024-04-01', 3600000, 'INR'),
(7, '2024-04-01', 4200000, 'INR'),
(8, '2024-04-01', 3400000, 'INR'),
(9, '2024-04-01', 1600000, 'INR'),
(10, '2024-04-01', 900000, 'INR');
