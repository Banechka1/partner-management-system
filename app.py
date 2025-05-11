from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import csv
import os
import chardet
import pandas as pd


app = Flask(__name__)

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    with app.open_resource('schema.sql', mode='r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


@app.route('/')
def index():
    conn = get_db_connection()
    
    # Получаем список партнеров
    partners = conn.execute('SELECT * FROM Partners').fetchall()
    
    # Получаем общее количество продаж для каждого партнера
    sales_data = conn.execute('''
        SELECT PartnerID, SUM(Quantity) AS TotalQuantity
        FROM SalesHistory
        GROUP BY PartnerID
    ''').fetchall()
    
    # Преобразуем данные в словарь для удобства
    sales_dict = {row['PartnerID']: row['TotalQuantity'] for row in sales_data}
    
    conn.close()
    
    # Рассчитываем скидку для каждого партнера
    partners_with_discount = []
    for partner in partners:
        total_quantity = sales_dict.get(partner['PartnerID'], 0)
        discount = calculate_discount(total_quantity)
        partners_with_discount.append({
            'PartnerID': partner['PartnerID'],
            'Name': partner['Name'],
            'Type': partner['Type'],
            'Rating': partner['Rating'],
            'DirectorName': partner['DirectorName'],
            'Phone': partner['Phone'],
            'Email': partner['Email'],
            'Address': partner['Address'],
            'RegistrationDate': partner['RegistrationDate'],
            'TotalQuantity': total_quantity,
            'Discount': discount
        })
    
    return render_template('index.html', partners=partners_with_discount)

# Функция расчета скидки
def calculate_discount(total_quantity):
    if total_quantity < 10000:
        return 0
    elif 10000 <= total_quantity < 50000:
        return 5
    elif 50000 <= total_quantity < 300000:
        return 10
    else:
        return 15


@app.route('/add_partner_form', methods=['GET', 'POST'])
def add_partner_form():
    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form['name']
        partner_type = request.form['type']
        rating = request.form['rating']
        address = request.form['address']
        director_name = request.form['director_name']
        phone = request.form['phone']
        email = request.form['email']

        # Проверяем корректность данных
        try:
            rating = int(rating)
            if rating < 0:
                raise ValueError("Рейтинг должен быть неотрицательным числом.")
        except ValueError as e:
            return render_template('error.html', message=str(e))

        # Добавляем партнера в базу данных
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO Partners (Name, Type, Rating, Address, DirectorName, Phone, Email, RegistrationDate)
            VALUES (?, ?, ?, ?, ?, ?, ?, date('now'))
        ''', (name, partner_type, rating, address, director_name, phone, email))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    # Отображаем форму добавления партнера
    return render_template('add_partner_form.html')

@app.route('/edit_partner_form/<int:partner_id>', methods=['GET', 'POST'])
def edit_partner_form(partner_id):
    conn = get_db_connection()

    if request.method == 'POST':
        # Получаем данные из формы
        name = request.form['name']
        partner_type = request.form['type']
        rating = request.form['rating']
        address = request.form['address']
        director_name = request.form['director_name']
        phone = request.form['phone']
        email = request.form['email']

        # Проверяем корректность данных
        try:
            rating = int(rating)
            if rating < 0:
                raise ValueError("Рейтинг должен быть неотрицательным числом.")
        except ValueError as e:
            return render_template('error.html', message=str(e))

        # Обновляем данные партнера
        conn.execute('''
            UPDATE Partners
            SET Name = ?, Type = ?, Rating = ?, Address = ?, DirectorName = ?, Phone = ?, Email = ?
            WHERE PartnerID = ?
        ''', (name, partner_type, rating, address, director_name, phone, email, partner_id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    # Получаем данные партнера для формы редактирования
    partner = conn.execute('SELECT * FROM Partners WHERE PartnerID = ?', (partner_id,)).fetchone()
    conn.close()

    return render_template('edit_partner_form.html', partner=partner)


@app.route('/partner_sales/<int:partner_id>')
def partner_sales(partner_id):
    conn = get_db_connection()
    sales = conn.execute('''
        SELECT SalesHistory.SaleID, Products.Name AS ProductName, SalesHistory.Quantity, SalesHistory.SaleDate
        FROM SalesHistory
        JOIN Products ON SalesHistory.ProductID = Products.ProductID
        WHERE SalesHistory.PartnerID = ?
    ''', (partner_id,)).fetchall()
    conn.close()
    return render_template('partner_sales.html', sales=sales)


def import_data():
    conn = get_db_connection()

    # Список таблиц и соответствующих файлов
    tables = {
        "Partners": "partners.xlsx",
        "Products": "products.xlsx",
        "SalesHistory": "sales_history.xlsx"
    }

    for table_name, file_name in tables.items():
        if not os.path.exists(file_name):
            print(f'Таблица {table_name} для импорта не найдена.')
            continue

        try:
            # Читаем данные из Excel-файла
            df = pd.read_excel(file_name)

            # Проверяем, что количество столбцов соответствует ожидаемому
            if table_name == "Partners":
                expected_columns = ['PartnerID', 'Name', 'Phone', 'Email', 'Address', 'RegistrationDate']
            elif table_name == "Products":
                expected_columns = ['ProductID', 'Name', 'Description', 'Price']
            elif table_name == "SalesHistory":
                expected_columns = ['SaleID', 'PartnerID', 'ProductID', 'Quantity', 'SaleDate']

            if not all(col in df.columns for col in expected_columns):
                print(f'Ошибка: Неверные столбцы в файле {file_name}.')
                continue

            # Импортируем данные в базу
            for _, row in df.iterrows():
                if table_name == "Partners":
                    conn.execute('INSERT OR REPLACE INTO Partners (PartnerID, Name, Phone, Email, Address, RegistrationDate) VALUES (?, ?, ?, ?, ?, ?)',
                                 (row['PartnerID'], row['Name'], row['Phone'], row['Email'], row['Address'], row['RegistrationDate']))
                elif table_name == "Products":
                    conn.execute('INSERT OR REPLACE INTO Products (ProductID, Name, Description, Price) VALUES (?, ?, ?, ?)',
                                 (row['ProductID'], row['Name'], row['Description'], row['Price']))
                elif table_name == "SalesHistory":
                    conn.execute('INSERT OR REPLACE INTO SalesHistory (SaleID, PartnerID, ProductID, Quantity, SaleDate) VALUES (?, ?, ?, ?, ?)',
                                 (row['SaleID'], row['PartnerID'], row['ProductID'], row['Quantity'], row['SaleDate']))

            print(f'Таблица {table_name} успешно импортирована!')

        except Exception as e:
            print(f'Ошибка при импорте таблицы {table_name}: {e}')
            conn.rollback()  # Откат транзакции в случае ошибки

    conn.commit()
    conn.close()



if __name__ == '__main__':
    init_db()  # Инициализация базы данных
    import_data()
    app.run(debug=True)