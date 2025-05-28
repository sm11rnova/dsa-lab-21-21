CREATE TABLE IF NOT EXISTS currencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    currency_name VARCHAR UNIQUE,         
    rate NUMERIC                          
);
