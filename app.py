from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Dùng để quản lý thông báo flash


# Hàm kết nối đến database
def connect_to_db(username, password):
    try:
        connection = psycopg2.connect(
            dbname="baitap1",
            user=username,
            password=password,
            host="localhost"
        )
        return connection
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        return None

# Trang đăng nhập
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = connect_to_db(username, password)
        if connection:
            # Lưu thông tin đăng nhập vào session hoặc truyền qua query string
            return redirect(url_for('menu', username=username, password=password))
        else:
            flash("Đăng nhập thất bại. Kiểm tra thông tin đăng nhập.", "error")
    return render_template('login.html')

# Trang Menu Quản Lý Sản Phẩm sau khi đăng nhập thành công
@app.route('/menu')
def menu():
    username = request.args.get('username')
    password = request.args.get('password')
    return render_template('menu.html', username=username, password=password)

# Trang tìm kiếm sản phẩm
@app.route('/search', methods=['GET', 'POST'])
def search_product():
    results = None
    username = request.args.get('username')
    password = request.args.get('password')
    connection = connect_to_db(username, password)
    
    if request.method == 'POST' and connection:
        product_name = request.form['product_name']
        cursor = connection.cursor()
        query = "SELECT * FROM products WHERE product_name ILIKE %s"
        cursor.execute(query, ('%' + product_name + '%',))
        results = cursor.fetchall()
        cursor.close()
    return render_template('search.html', results=results)

 # Trang thêm sản phẩm mới
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    username = request.args.get('username')
    password = request.args.get('password')
    connection = connect_to_db(username, password)
    
    if request.method == 'POST' and connection:
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        category_id = request.form['category_id']
        
        try:
            cursor = connection.cursor()
            query = "INSERT INTO products (product_name, product_price, category_id) VALUES (%s, %s, %s)"
            cursor.execute(query, (product_name, product_price, category_id))
            connection.commit()
            flash("Sản phẩm đã được thêm thành công!", "success")
        
        except psycopg2.Error as e:
            flash("Thêm sản phẩm thất bại. Vui lòng thử lại.", "error")
            connection.rollback()
        
        finally:
            cursor.close()
    
    return render_template('add_product.html')

if __name__ == '__main__':
    app.run(debug=True)