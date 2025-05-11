CREATE TABLE IF NOT EXISTS Partners (
    PartnerID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Type TEXT NOT NULL DEFAULT 'Клиент',
    Rating INTEGER NOT NULL DEFAULT 0 CHECK (Rating >= 0),
    Address TEXT,
    DirectorName TEXT,
    Phone TEXT,
    Email TEXT,
    RegistrationDate DATE
);

CREATE TABLE IF NOT EXISTS Products (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Description TEXT,
    Price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS SalesHistory (
    SaleID INTEGER PRIMARY KEY AUTOINCREMENT,
    PartnerID INTEGER NOT NULL,
    ProductID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL,
    SaleDate DATE NOT NULL,
    FOREIGN KEY (PartnerID) REFERENCES Partners(PartnerID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);