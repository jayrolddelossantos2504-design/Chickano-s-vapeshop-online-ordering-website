from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, stream_with_context, json
import json
import mysql.connector
from datetime import datetime, time as dt_time
import time
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__, template_folder='Templates', static_folder='static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'your_secret_key'

# ✅ MySQL connection (no global cursor)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="capstone"
)

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.endpoint))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# ---------------- INDEX ----------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        f_name = request.form.get('f_name')
        m_name = request.form.get('m_name')
        l_name = request.form.get('l_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role_id = 2  # Default role for customers

        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user (F_Name, M_Name, L_Name, RoleID)
                    VALUES (%s, %s, %s, %s)
                """, (f_name, m_name, l_name, role_id))
                db.commit()
                user_id = cursor.lastrowid

                cursor.execute("INSERT INTO email (Email, UserID) VALUES (%s, %s)", (email, user_id))
                cursor.execute("INSERT INTO password (Password, UserID) VALUES (%s, %s)", (password, user_id))
                db.commit()

            flash('User registered successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.rollback()
            flash(f"Error: {e}", 'danger')

    return render_template('signup.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    SELECT u.UserID, u.RoleID
                    FROM user u
                    JOIN email e ON u.UserID = e.UserID
                    JOIN password p ON u.UserID = p.UserID
                    WHERE e.Email = %s AND p.Password = %s
                """, (email, password))
                user = cursor.fetchone()

            if user:
                session['user_id'] = user[0]
                session['email'] = email
                session['role_id'] = int(user[1])

                flash('Login successful!', 'success')
                
                # Check for next parameter
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                    
                # If no next parameter, redirect based on role ID
                role_id = int(user[1])
                if role_id == 1:
                    return redirect(url_for('dashboard'))
                elif role_id == 2:
                    return redirect(url_for('products'))
                elif role_id == 3:
                    return redirect(url_for('emp_dashboard'))
                else:
                    return redirect(url_for('products'))  # Default fallback
            else:
                flash('Invalid email or password.', 'danger')
        except Exception as e:
            flash(f"Login error: {e}", 'danger')

    return render_template('login.html')


# ---------------- EMPLOYEE DASHBOARD ----------------
@app.route('/emp_dashboard')
@login_required
def emp_dashboard():
    if session.get('role_id') != 3:
        flash("Access denied. Employee access only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor(dictionary=True) as cur:
            # Get total orders count
            cur.execute("SELECT COUNT(*) AS total_orders FROM `order`")
            total_orders = cur.fetchone()["total_orders"]

            # Get order counts by status
            cur.execute("""
                SELECT Order_Status, COUNT(*) as count 
                FROM `order` 
                GROUP BY Order_Status
            """)
            # Initialize with only the statuses we want to show
            order_status_counts = {
                'Pending': 0,
                'Approved': 0,
                'Cancelled': 0
            }
            # Update with actual counts from the database
            for row in cur.fetchall():
                if row['Order_Status'] in order_status_counts:
                    order_status_counts[row['Order_Status']] = row['count']

            # Get total transactions count
            cur.execute("SELECT COUNT(*) AS total_transactions FROM transaction")
            total_transactions = cur.fetchone()["total_transactions"]

            # Get recent orders
            cur.execute("""
                SELECT o.OrderID, o.Order_Date, 
                       CONCAT(u.F_Name, ' ', u.L_Name) as customer_name,
                       e.Email as customer_email,
                       o.Order_Status,
                       (SELECT COUNT(*) FROM order_details WHERE OrderID = o.OrderID) as item_count,
                       (SELECT SUM(od.Quantity * p.Price) 
                        FROM order_details od 
                        JOIN product p ON od.ProductID = p.ProductID 
                        WHERE od.OrderID = o.OrderID) as total_amount
                FROM `order` o
                JOIN user u ON o.UserID = u.UserID
                JOIN email e ON u.UserID = e.UserID
                ORDER BY o.Order_Date DESC
                LIMIT 5
            """)
            recent_orders = cur.fetchall()

            # Get low stock products
            cur.execute("""
                SELECT p.Product_Name, p.Stock, c.Category_Name 
                FROM product p
                JOIN category c ON p.CategoryID = c.CategoryID
                WHERE p.Stock < 5
                ORDER BY p.Stock ASC
                LIMIT 5
            """)
            low_stock = cur.fetchall()

            # Get total stock count
            cur.execute("SELECT SUM(Stock) AS total_stock FROM product")
            stock_count = cur.fetchone()["total_stock"] or 0

            # Get stock by category
            cur.execute("""
                SELECT 
                    c.Category_Name,
                    COALESCE(SUM(p.Stock), 0) as category_stock
                FROM category c
                LEFT JOIN product p ON c.CategoryID = p.CategoryID
                GROUP BY c.CategoryID, c.Category_Name
                ORDER BY c.Category_Name
            """)
            stock_by_category = {row['Category_Name']: row['category_stock'] for row in cur.fetchall()}

        return render_template(
            "emp_dashboard.html",
            order_count=total_orders,
            transaction_count=total_transactions,
            order_status_counts=order_status_counts,
            recent_orders=recent_orders,
            stock_count=stock_count,
            stock_by_category=stock_by_category,
            low_stock=low_stock,
            sales_labels=[],  # These would be needed if you have sales charts
            sales_values=[]   # These would be needed if you have sales charts
        )
    except Exception as e:
        flash(f"Error loading dashboard: {e}", "danger")
        return redirect(url_for('index'))

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ---------------- LIGHT THEME PRODUCTS PAGE ----------------
@app.route('/LT_Products')
@login_required
def LT_Products():
    """Light theme version of the products page"""
    if session.get('role_id') != 2:
        flash("Access denied. Customers only.", "danger")
        return redirect(url_for('login'))

    selected_category_id = request.args.get('category')
    search_query = request.args.get('search')
    sort_option = request.args.get('sort')  # price_asc, price_desc, stock_asc, stock_desc, top_sales
    products, categories = [], []

    try:
        with db.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT CategoryID, Category_Name FROM category")
            categories = cursor.fetchall()

            query = """
                SELECT p.ProductID AS id,
                       p.Product_Name AS name,
                       p.Description AS description,
                       p.Price AS price,
                       p.Stock AS stock,
                       p.Image_url AS image_url,
                       COALESCE(s.total_sold, 0) AS total_sold
                FROM product p
                LEFT JOIN (
                    SELECT od.ProductID, SUM(od.Quantity) AS total_sold
                    FROM order_details od
                    JOIN `order` o ON o.OrderID = od.OrderID
                    WHERE o.Order_Status = 'Approved'
                    GROUP BY od.ProductID
                ) s ON s.ProductID = p.ProductID
            """
            conditions, params = [], []

            if selected_category_id:
                conditions.append("p.CategoryID = %s")
                params.append(selected_category_id)
            if search_query:
                conditions.append("(p.Product_Name LIKE %s OR p.Description LIKE %s)")
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            if sort_option == 'price_asc':
                query += " ORDER BY p.Price ASC"
            elif sort_option == 'price_desc':
                query += " ORDER BY p.Price DESC"
            elif sort_option == 'stock_asc':
                query += " ORDER BY p.Stock ASC"
            elif sort_option == 'stock_desc':
                query += " ORDER BY p.Stock DESC"
            elif sort_option == 'top_sales':
                query += " ORDER BY total_sold DESC, p.ProductID DESC"
            else:
                query += " ORDER BY p.ProductID DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

        for row in rows:
            products.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "price": row["price"],
                "stock": row["stock"],
                "image_url": row["image_url"],
                "total_sold": row["total_sold"],
            })

    except Exception as e:
        flash(f"Could not load products: {e}", "danger")

    return render_template(
        'LT_Products.html',
        products=products,
        categories=categories,
        selected_category_id=selected_category_id,
        search_query=search_query,
        sort_option=sort_option,
        user_email=session.get('email')
    )

# ---------------- PRODUCTS PAGE ----------------
@app.route('/products')
@login_required
def products():
    if session.get('role_id') != 2:
        flash("Access denied. Customers only.", "danger")
        return redirect(url_for('login'))

    selected_category_id = request.args.get('category')
    search_query = request.args.get('search')
    sort_option = request.args.get('sort')  # price_asc, price_desc, stock_asc, stock_desc, top_sales
    products, categories = [], []

    try:
        with db.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT CategoryID, Category_Name FROM category")
            categories = cursor.fetchall()

            query = """
                SELECT p.ProductID AS id,
                       p.Product_Name AS name,
                       p.Description AS description,
                       p.Price AS price,
                       p.Stock AS stock,
                       p.Image_url AS image_url,
                       COALESCE(s.total_sold, 0) AS total_sold
                FROM product p
                LEFT JOIN (
                    SELECT od.ProductID, SUM(od.Quantity) AS total_sold
                    FROM order_details od
                    JOIN `order` o ON o.OrderID = od.OrderID
                    WHERE o.Order_Status = 'Approved'
                    GROUP BY od.ProductID
                ) s ON s.ProductID = p.ProductID
            """
            conditions, params = [], []

            if selected_category_id:
                conditions.append("p.CategoryID = %s")
                params.append(selected_category_id)
            if search_query:
                conditions.append("(p.Product_Name LIKE %s OR p.Description LIKE %s)")
                params.extend([f"%{search_query}%", f"%{search_query}%"])

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            if sort_option == 'price_asc':
                query += " ORDER BY p.Price ASC"
            elif sort_option == 'price_desc':
                query += " ORDER BY p.Price DESC"
            elif sort_option == 'stock_asc':
                query += " ORDER BY p.Stock ASC"
            elif sort_option == 'stock_desc':
                query += " ORDER BY p.Stock DESC"
            elif sort_option == 'top_sales':
                query += " ORDER BY total_sold DESC, p.ProductID DESC"
            else:
                query += " ORDER BY p.ProductID DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

        for row in rows:
            products.append({
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "price": row["price"],
                "stock": row["stock"],
                "image_url": row["image_url"],
                "total_sold": row["total_sold"],
            })

    except Exception as e:
        flash(f"Could not load products: {e}", "danger")

    return render_template(
        'products.html',
        products=products,
        categories=categories,
        selected_category_id=selected_category_id,
        search_query=search_query,
        sort_option=sort_option,
        user_email=session.get('email')
    )


# ---------------- PRODUCT DETAIL ----------------
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    if session.get('role_id') != 2:
        flash("Access denied. Customers only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT Product_Name, Description, Price, Stock, Image_url, CategoryID
                FROM product WHERE ProductID = %s
            """, (product_id,))
            row = cursor.fetchone()

            if not row:
                flash("Product not found.", "warning")
                return redirect(url_for('products'))

            product = {
                "id": product_id,
                "name": row[0],
                "description": row[1],
                "price": row[2],
                "stock": row[3],
                "image_url": row[4],
                "category_id": row[5]
            }

            cursor.execute("""
                SELECT ProductID, Product_Name, Description, Price, Image_url
                FROM product
                WHERE CategoryID = %s AND ProductID != %s
                LIMIT 4
            """, (product["category_id"], product_id))
            related_products = cursor.fetchall()

        related_list = [{
            "id": r[0], "name": r[1], "description": r[2], "price": r[3], "image_url": r[4]
        } for r in related_products]

        return render_template('product_detail.html',
                               product=product,
                               related_products=related_list,
                               user_email=session.get('email'))
    except Exception as e:
        flash(f"Could not load product: {e}", "danger")
        return redirect(url_for('products'))

# ---------------- LIGHT THEME PRODUCT DETAIL ----------------
@app.route('/LT_Product_details/<int:product_id>')
@app.route('/LT_product/<int:product_id>', endpoint='LT_product_alt')  # For backward compatibility
def LT_Product_details(product_id):
    if 'user_id' not in session:
        flash("Please log in to view product details.", "warning")
        return redirect(url_for('login', next=request.url))
        
    if session.get('role_id') != 2:
        flash("Access denied. Customers only.", "danger")
        return redirect(url_for('products'))

    try:
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT Product_Name, Description, Price, Stock, Image_url, CategoryID
                FROM product WHERE ProductID = %s
            """, (product_id,))
            row = cursor.fetchone()

            if not row:
                flash("Product not found.", "warning")
                return redirect(url_for('LT_Products'))

            product = {
                "id": product_id,
                "name": row[0],
                "description": row[1],
                "price": row[2],
                "stock": row[3],
                "image_url": row[4],
                "category_id": row[5]
            }

            cursor.execute("""
                SELECT ProductID, Product_Name, Description, Price, Image_url
                FROM product
                WHERE CategoryID = %s AND ProductID != %s
                LIMIT 4
            """, (product["category_id"], product_id))
            related_products = cursor.fetchall()

        related_list = [{
            "id": r[0], "name": r[1], "description": r[2], "price": r[3], "image_url": r[4]
        } for r in related_products]

        return render_template('LT_Product_details.html',
                               product=product,
                               related_products=related_list,
                               user_email=session.get('email'))
    except Exception as e:
        flash(f"Could not load product: {e}", "danger")
        return redirect(url_for('LT_Products'))


# ---------------- CUSTOMER: ADD TO ORDER ----------------

@app.route('/add_to_order', methods=['POST'])
def add_to_order():
    if session.get('role_id') != 2:
        flash("Access denied. Customers only.", "danger")
        return redirect(url_for('login'))

    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', type=int)
    user_id = session.get('user_id')

    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    try:
        with db.cursor(dictionary=True) as cur:
            # ✅ Find an existing pending order for this user
            cur.execute("""
                SELECT OrderID FROM `order`
                WHERE UserID = %s AND Order_Status = 'Pending'
            """, (user_id,))
            existing_order = cur.fetchone()

            if existing_order:
                order_id = existing_order["OrderID"]
            else:
                # ✅ Create a new order if none exist
                cur.execute("""
                    INSERT INTO `order` (Order_Date, Order_Status, Pickup_Status, UserID)
                    VALUES (CURDATE(), 'Pending', 'Pending', %s)
                """, (user_id,))
                db.commit()
                order_id = cur.lastrowid

            # ✅ Insert the product into order_details
            cur.execute("""
                INSERT INTO order_details (ProductID, OrderID, Quantity)
                VALUES (%s, %s, %s)
            """, (product_id, order_id, quantity))
            db.commit()

        # ✅ Use SweetAlert2 trigger instead of flash
        session["swal"] = {
            "title": "Added to Order!",
            "text": "✅ Your item has been added successfully.",
            "icon": "success"
        }

        # Check if the request came from the light theme
        is_light_theme = request.form.get('is_light_theme') == 'true'
        if is_light_theme:
            return redirect(url_for('LT_Product_details', product_id=product_id))
        else:
            return redirect(url_for('product_detail', product_id=product_id))

    except Exception as e:
        db.rollback()
        print(f"[ERROR] add_to_order: {e}")
        session["swal"] = {
            "title": "Error",
            "text": f"❌ Could not add to order: {e}",
            "icon": "error"
        }
        return redirect(url_for('product_detail', product_id=product_id))


# ---------------- CUSTOMER: MY ORDERS ----------------
@app.route('/my_orders')
def my_orders():
    if session.get('role_id') != 2:
        flash("Access denied. Customers only.", "danger")
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    try:
        with db.cursor(dictionary=True) as cur:
            # Fetch all orders for this user
            cur.execute("""
                SELECT o.OrderID, o.Order_Date, o.Order_Status, o.Pickup_Status,
                       SUM(od.Quantity * p.Price) AS TotalPrice
                FROM `order` o
                JOIN order_details od ON o.OrderID = od.OrderID
                JOIN product p ON od.ProductID = p.ProductID
                WHERE o.UserID = %s
                GROUP BY o.OrderID
                ORDER BY o.Order_Date DESC
            """, (user_id,))
            orders = cur.fetchall()

        if not orders:
            orders = []

        from datetime import datetime, time
        for o in orders:
            order_id = o["OrderID"]

            # Fetch all line items
            with db.cursor(dictionary=True) as cur:
                cur.execute("""
                    SELECT p.ProductID,
                           p.Product_Name AS name,
                           p.Image_url AS image,
                           od.Quantity AS quantity,
                           p.Price AS price
                    FROM order_details od
                    JOIN product p ON od.ProductID = p.ProductID
                    WHERE od.OrderID = %s
                """, (order_id,))
                o["items"] = cur.fetchall()

            # Time logic (for future use)
            order_dt = o["Order_Date"]
            if order_dt and not isinstance(order_dt, datetime):
                order_dt = datetime.combine(order_dt, time.min)
            elapsed = (datetime.now() - order_dt).total_seconds() if order_dt else 0
            remaining = max(0, 600 - int(elapsed))
            o["remaining_seconds"] = remaining

            # ✅ FIX: show edit button for all pending orders (ignore time for now)
            o["can_edit"] = o["Order_Status"] == "Pending"

        # ✅ Optional: print debug info in server logs
        print("\n=== DEBUG: My Orders ===")
        for o in orders:
            print(f"Order {o['OrderID']}: Status={o['Order_Status']}, Remaining={o['remaining_seconds']}, Can_Edit={o['can_edit']}")
        print("========================\n")

        return render_template("my_orders.html", orders=orders, user_email=session.get("email"))

    except Exception as e:
        print(f"❌ ERROR in /my_orders route: {e}")
        flash(f"Could not load your orders: {e}", "danger")
        return render_template("my_orders.html", orders=[], user_email=session.get("email"))


# ---------------- CUSTOMER: LIGHT THEME MY ORDERS ----------------
@app.route('/LT_my_orders')
def LT_my_orders():
    if session.get('role_id') != 2:
        flash("Access denied. Customers only.", "danger")
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    try:
        with db.cursor(dictionary=True) as cur:
            # Fetch all orders for this user
            cur.execute("""
                SELECT o.OrderID, o.Order_Date, o.Order_Status, o.Pickup_Status,
                       SUM(od.Quantity * p.Price) AS TotalPrice
                FROM `order` o
                JOIN order_details od ON o.OrderID = od.OrderID
                JOIN product p ON od.ProductID = p.ProductID
                WHERE o.UserID = %s
                GROUP BY o.OrderID
                ORDER BY o.Order_Date DESC
            """, (user_id,))
            orders = cur.fetchall()

        if not orders:
            orders = []

        from datetime import datetime, time
        for o in orders:
            order_id = o["OrderID"]

            # Fetch all line items
            with db.cursor(dictionary=True) as cur:
                cur.execute("""
                    SELECT p.ProductID,
                           p.Product_Name AS name,
                           p.Image_url AS image,
                           od.Quantity AS quantity,
                           p.Price AS price
                    FROM order_details od
                    JOIN product p ON od.ProductID = p.ProductID
                    WHERE od.OrderID = %s
                """, (order_id,))
                o["items"] = cur.fetchall()

            # Time logic (for future use)
            order_dt = o["Order_Date"]
            if order_dt and not isinstance(order_dt, datetime):
                order_dt = datetime.combine(order_dt, time.min)
            elapsed = (datetime.now() - order_dt).total_seconds() if order_dt else 0
            remaining = max(0, 600 - int(elapsed))
            o["remaining_seconds"] = remaining

            # Show edit button for all pending orders
            o["can_edit"] = o["Order_Status"] == "Pending"

        print("\n=== DEBUG: LT_My Orders ===")
        for o in orders:
            print(f"Order {o['OrderID']}: Status={o['Order_Status']}, Remaining={o['remaining_seconds']}, Can_Edit={o['can_edit']}")
        print("========================\n")

        return render_template("LT_my_orders.html", 
                             orders=orders, 
                             user_email=session.get("email"))

    except Exception as e:
        print(f"❌ ERROR in /LT_my_orders route: {e}")
        flash(f"Could not load your orders: {e}", "danger")
        return render_template("LT_my_orders.html", 
                             orders=[], 
                             user_email=session.get("email"))


# ---------------- CUSTOMER: CANCEL ORDER ----------------

@app.route('/cancel_order/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    if session.get('role_id') != 2:
        flash("Access denied. Customers only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor() as cur:
            # ✅ Cancel only if still pending
            cur.execute("""
                UPDATE `order`
                SET Order_Status = 'Cancelled', Pickup_Status = 'Cancelled'
                WHERE OrderID = %s AND Order_Status = 'Pending'
            """, (order_id,))
            db.commit()

            if cur.rowcount > 0:
                # ✅ Success — show SweetAlert
                session["swal"] = {
                    "title": "Order Cancelled",
                    "text": "❌ Your order has been successfully cancelled.",
                    "icon": "success"
                }
            else:
                # ⚠️ Order not pending or not found
                session["swal"] = {
                    "title": "Action Not Allowed",
                    "text": "⚠️ Only pending orders can be cancelled.",
                    "icon": "warning"
                }

    except Exception as e:
        db.rollback()
        print(f"[ERROR] cancel_order: {e}")
        session["swal"] = {
            "title": "Error",
            "text": f"❌ Could not cancel your order: {e}",
            "icon": "error"
        }
        
    return redirect(url_for('my_orders'))

# ---------------- CUSTOMER: EDIT ORDER ----------------
@app.route('/edit_order/<int:order_id>', methods=['GET', 'POST'])
def edit_order(order_id):
    if session.get('role_id') != 2:
        flash("Access denied. Customers only.", "danger")
        return redirect(url_for('login'))

    user_id = session.get('user_id')

    try:
        with db.cursor(dictionary=True) as cur:
            # --- Fetch the main order info ---
            cur.execute("""
                SELECT o.OrderID, o.UserID, o.Order_Date, o.Order_Status
                FROM `order` o
                WHERE o.OrderID = %s AND o.UserID = %s
            """, (order_id, user_id))
            order = cur.fetchone()

        if not order:
            flash("❌ Order not found or unauthorized access.", "danger")
            return redirect(url_for('my_orders'))

        # --- Fetch all items for that order ---
        with db.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT 
                    p.ProductID,
                    p.Product_Name AS name,
                    p.Image_url AS image,
                    p.Stock AS Stock,
                    p.Price AS Price,
                    od.Quantity AS Quantity
                FROM order_details od
                JOIN product p ON od.ProductID = p.ProductID
                WHERE od.OrderID = %s
            """, (order_id,))
            items = cur.fetchall()

        # --- Calculate total amount ---
        total = sum(item["Price"] * item["Quantity"] for item in items)
        order["TotalPrice"] = total

        # --- If POST, update quantities ---
        if request.method == 'POST':
            try:
                with db.cursor() as cur:
                    for item in items:
                        field_name = f"quantity_{item['ProductID']}"
                        if field_name in request.form:
                            new_qty = int(request.form[field_name])

                            if new_qty <= 0:
                                cur.execute("""
                                    DELETE FROM order_details
                                    WHERE OrderID = %s AND ProductID = %s
                                """, (order_id, item['ProductID']))
                            else:
                                cur.execute("""
                                    UPDATE order_details
                                    SET Quantity = %s
                                    WHERE OrderID = %s AND ProductID = %s
                                """, (new_qty, order_id, item['ProductID']))
                    db.commit()
                flash("✅ Order updated successfully!", "success")
                # Check if the request came from the light theme by checking the form data
                if request.form.get('from_light_theme') == 'true':
                    return redirect(url_for('LT_my_orders'))
                return redirect(url_for('my_orders'))

            except Exception as inner_e:
                db.rollback()
                flash(f"❌ Error updating order: {inner_e}", "danger")
                print(f"[DEBUG edit_order POST error] {inner_e}")
                # Check if the request came from the light theme by checking the form data
                if request.form.get('from_light_theme') == 'true':
                    return redirect(url_for('LT_my_orders'))
                return redirect(url_for('my_orders'))

        # --- Render the edit page ---
        return render_template('edit_order.html', order=order, items=items)

    except Exception as e:
        db.rollback()
        flash(f"❌ Error loading edit order page: {e}", "danger")
        print(f"[DEBUG edit_order error] {e}")
        return redirect(url_for('my_orders'))



# ---------------- CUSTOMER: Remove ORDER ----------------

@app.route('/remove_order_item/<int:order_id>/<int:product_id>', methods=['POST'])
def remove_order_item(order_id, product_id):
    if session.get('role_id') != 2:
        return jsonify({"success": False, "message": "Access denied. Customers only."}), 403
    
    try:
        with db.cursor() as cur:
            # Check if order is still pending and belongs to the user
            cur.execute("""
                SELECT o.UserID, o.Order_Status, od.Quantity, p.Price 
                FROM `order` o
                JOIN order_details od ON o.OrderID = od.OrderID
                JOIN product p ON od.ProductID = p.ProductID
                WHERE o.OrderID = %s AND od.ProductID = %s
            """, (order_id, product_id))
            
            order_item = cur.fetchone()
            
            if not order_item:
                return jsonify({"success": False, "message": "Order item not found."}), 404
                
            if order_item[0] != session.get('user_id'):
                return jsonify({"success": False, "message": "Access denied. This is not your order."}), 403
                
            if order_item[1] != 'Pending':
                return jsonify({"success": False, "message": "Only items in pending orders can be removed."}), 400
            
            # Remove the item from order_details
            cur.execute("""
                DELETE FROM order_details 
                WHERE OrderID = %s AND ProductID = %s
            """, (order_id, product_id))
            
            # Update the order total
            cur.execute("""
                UPDATE `order` o
                SET Total_Amount = (
                    SELECT COALESCE(SUM(od.Quantity * p.Price), 0)
                    FROM order_details od
                    JOIN product p ON od.ProductID = p.ProductID
                    WHERE od.OrderID = %s
                )
                WHERE o.OrderID = %s
            """, (order_id, order_id))
            
            # If no items left in the order, cancel the order
            cur.execute("""
                SELECT COUNT(*) FROM order_details WHERE OrderID = %s
            """, (order_id,))
            
            if cur.fetchone()[0] == 0:
                cur.execute("""
                    UPDATE `order` 
                    SET Order_Status = 'Cancelled', 
                        Pickup_Status = 'Cancelled',
                        Total_Amount = 0
                    WHERE OrderID = %s
                """, (order_id,))
            
            db.commit()
            
            return jsonify({
                "success": True, 
                "message": "Item removed successfully.",
                "order_empty": cur.rowcount == 0
            })
            
    except Exception as e:
        db.rollback()
        print(f"[ERROR] remove_order_item: {e}")
        return jsonify({"success": False, "message": f"Could not remove item: {str(e)}"}), 500

    return redirect(url_for('my_orders'))



# ---------------- DOWNLOAD ORDER DETAILS (Styled PDF with Logo Left + Light Black) ----------------
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import io
import os

@app.route('/download_order/<int:order_id>')
def download_order(order_id):
    user_id = session.get('user_id')

    with db.cursor(dictionary=True) as cursor:
        cursor.execute("""
            SELECT o.Order_Status, o.Pickup_Status, o.Order_Date,
                   u.F_Name, u.L_Name, e.Email
            FROM `order` o
            JOIN user u ON o.UserID = u.UserID
            JOIN email e ON u.UserID = e.UserID
            WHERE o.OrderID = %s AND o.UserID = %s
        """, (order_id, user_id))
        order_info = cursor.fetchone()

        if not order_info or order_info["Order_Status"] != "Approved":
            flash("Order details are only available for approved orders.", "warning")
            return redirect(url_for('my_orders'))

        cursor.execute("""
            SELECT p.Product_Name, od.Quantity, p.Price
            FROM order_details od
            JOIN product p ON od.ProductID = p.ProductID
            WHERE od.OrderID = %s
        """, (order_id,))
        order_details = cursor.fetchall()

    # ✅ Create PDF
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # --- BRAND COLOR (Light Black) ---
    brand_color = colors.HexColor("#2b2b2b")

    # ---------- HEADER ----------
    pdf.setFillColor(brand_color)
    pdf.rect(0, height - 80, width, 80, fill=True, stroke=False)

    # ✅ Add Logo (Top Left)
    try:
        logo_path = r"C:\Users\ACER\Downloads\Capstone-20251025T015635Z-1-001\Capstone\static\images\logo.png"
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            pdf.drawImage(logo, 40, height - 75, width=100, height=60, mask='auto')
    except Exception as e:
        print(f"Logo not found or failed to load: {e}")

    # ✅ Header Text (Right Side)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(160, height - 45, "Chickano's Vapeshop")

    # ---------- ORDER INFO ----------
    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, height - 110, "Order Details")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, height - 130, f"Order ID: {order_id}")
    pdf.drawString(50, height - 145, f"Customer: {order_info['F_Name']} {order_info['L_Name']}")
    pdf.drawString(50, height - 160, f"Email: {order_info['Email']}")
    pdf.drawString(50, height - 175, f"Order Date: {order_info['Order_Date']}")

    # ---------- PRODUCT TABLE HEADER ----------
    y = height - 200
    pdf.setFont("Helvetica-Bold", 11)
    pdf.setFillColor(brand_color)
    pdf.rect(45, y - 5, width - 90, 20, fill=True, stroke=False)
    pdf.setFillColor(colors.white)
    pdf.drawString(55, y, "Product")
    pdf.drawString(275, y, "Qty")
    pdf.drawString(340, y, "Price")
    pdf.drawString(440, y, "Subtotal")

    # ---------- PRODUCT DETAILS ----------
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.black)
    y -= 25
    total = 0
    for row in order_details:
        if y < 100:
            pdf.showPage()
            y = height - 100
        subtotal = row['Quantity'] * row['Price']
        total += subtotal
        pdf.drawString(55, y, row['Product_Name'])
        pdf.drawString(280, y, str(row['Quantity']))
        pdf.drawRightString(400, y, f"₱{row['Price']:.2f}")
        pdf.drawRightString(520, y, f"₱{subtotal:.2f}")
        y -= 18

    # ---------- TOTAL BOX ----------
    y -= 10
    pdf.setStrokeColor(brand_color)
    pdf.setLineWidth(1)
    pdf.rect(45, y - 30, width - 90, 30, fill=False)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(380, y - 12, "Total:")
    pdf.drawRightString(520, y - 12, f"₱{total:.2f}")

    # ---------- FOOTER ----------
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.setFillColor(colors.gray)
    pdf.drawCentredString(width / 2, 40, "Thank you for shopping at Chickano's Vapeshop!")
    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(colors.HexColor("#aaaaaa"))
    pdf.drawCentredString(width / 2, 28, "www.chickanosvape.com")

    pdf.save()
    buffer.seek(0)

    return Response(
        buffer,
        mimetype='application/pdf',
        headers={"Content-Disposition": f"attachment;filename=orderdetails_{order_id}.pdf"}
    )



# ---------------- ABOUT PAGE ----------------
@app.route('/about')
def about():
    return render_template('about.html')

# ---------------- ADMIN: ORDER MANAGEMENT ----------------

@app.route('/order_management')
@login_required
def order_management():
    if session.get('role_id') not in [1, 3]:  # Allow both admin (1) and employee (3)
        flash("Access denied. Admins and employees only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor(dictionary=True) as cur:
            # Fetch summary of all orders
            cur.execute("""
                SELECT o.OrderID, o.Order_Date, o.Order_Status, o.Pickup_Status,
                       u.F_Name, u.L_Name, e.Email,
                       SUM(od.Quantity * p.Price) AS TotalPrice
                FROM `order` o
                JOIN user u ON o.UserID = u.UserID
                JOIN email e ON u.UserID = e.UserID
                JOIN order_details od ON o.OrderID = od.OrderID
                JOIN product p ON od.ProductID = p.ProductID
                GROUP BY o.OrderID
                ORDER BY o.Order_Date DESC
            """)
            orders_data = cur.fetchall()

        orders = []
        for order in orders_data:
            order_id = order["OrderID"]

            # Fetch individual order details (items)
            with db.cursor(dictionary=True) as cur:
                cur.execute("""
                    SELECT p.Product_Name AS name,
                           od.Quantity AS quantity,
                           p.Price AS price,
                           (od.Quantity * p.Price) AS subtotal
                    FROM order_details od
                    JOIN product p ON od.ProductID = p.ProductID
                    WHERE od.OrderID = %s
                """, (order_id,))
                items = cur.fetchall()

            # Check if the order has been recorded in transactions
            with db.cursor(dictionary=True) as cur:
                cur.execute("SELECT COUNT(*) AS in_txn FROM transaction WHERE OrderID = %s", (order_id,))
                in_txn = cur.fetchone()["in_txn"] > 0

            # Assemble final order dictionary
            orders.append({
                "id": order_id,
                "date": order["Order_Date"],
                "order_status": order["Order_Status"],
                "pickup_status": order["Pickup_Status"],
                "customer": f"{order['F_Name']} {order['L_Name']}",
                "email": order["Email"],
                "total": order["TotalPrice"],
                "details": items,
                "in_transaction": in_txn
            })

        return render_template("order_management.html", orders=orders)

    except Exception as e:
        flash(f"❌ Could not load orders: {e}", "danger")
        return render_template("order_management.html", orders=[])


# ---------------- ADMIN: APPROVE / DECLINE ORDER ----------------

@app.route('/update_order/<int:order_id>/<action>', methods=['POST'])
def update_order(order_id, action):
    if session.get('role_id') != 1:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor(dictionary=True) as cur:
            # ✅ Fetch order items
            cur.execute("""
                SELECT od.ProductID, od.Quantity, p.Stock
                FROM order_details od
                JOIN product p ON od.ProductID = p.ProductID
                WHERE od.OrderID = %s
            """, (order_id,))
            items = cur.fetchall()

            if not items:
                flash("Order not found or has no items.", "warning")
                return redirect(url_for('order_management'))

            if action == "approve":
                # ✅ Check stock first
                for item in items:
                    if item["Stock"] < item["Quantity"]:
                        flash("❌ Not enough stock to approve this order.", "danger")
                        return redirect(url_for('order_management'))

                # ✅ Deduct stock quantities
                for item in items:
                    cur.execute("""
                        UPDATE product
                        SET Stock = Stock - %s
                        WHERE ProductID = %s
                    """, (item["Quantity"], item["ProductID"]))

                # ✅ Update order + pickup statuses
                cur.execute("""
                    UPDATE `order`
                    SET Order_Status = 'Approved', Pickup_Status = 'Waiting for Pickup'
                    WHERE OrderID = %s
                """, (order_id,))

                db.commit()
                flash("✅ Order approved and marked as 'Waiting for Pickup'.", "success")

            elif action == "decline":
                # ✅ Decline order
                cur.execute("""
                    UPDATE `order`
                    SET Order_Status = 'Declined', Pickup_Status = 'Cancelled'
                    WHERE OrderID = %s
                """, (order_id,))
                db.commit()
                flash("⚠️ Order declined successfully.", "warning")

            else:
                flash("Invalid action.", "danger")

        return redirect(url_for('order_management'))

    except Exception as e:
        db.rollback()
        flash(f"❌ Error processing order: {e}", "danger")
        return redirect(url_for('order_management'))


# ---------------- ADMIN: UPDATE PICKUP STATUS ----------------

@app.route('/update_pickup/<int:order_id>/<status>', methods=['POST'])
def update_pickup(order_id, status):
    if session.get('role_id') != 1:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor(dictionary=True) as cur:
            # ✅ Get current order status
            cur.execute("""
                SELECT Order_Status, Pickup_Status, UserID
                FROM `order`
                WHERE OrderID = %s
            """, (order_id,))
            order = cur.fetchone()

            if not order:
                flash("Order not found.", "danger")
                return redirect(url_for('order_management'))

            # ✅ Only allow update if Approved
            if order["Order_Status"] != "Approved":
                flash("⚠️ Pickup status can only be updated for approved orders.", "warning")
                return redirect(url_for('order_management'))

            # ✅ Prevent double updates
            if order["Pickup_Status"] in ["Already Picked Up", "Cancelled"]:
                flash("ℹ️ This order is already finalized and cannot be changed.", "info")
                return redirect(url_for('order_management'))

            # ✅ Update pickup status
            cur.execute("""
                UPDATE `order` SET Pickup_Status = %s WHERE OrderID = %s
            """, (status, order_id))

            # ✅ If picked up → log transaction
            if status == "Already Picked Up":
                cur.execute("""
                    INSERT INTO transaction (Transaction_Date, Total_Price, OrderID, UserID)
                    SELECT CURDATE(),
                           SUM(od.Quantity * p.Price),
                           o.OrderID, o.UserID
                    FROM `order` o
                    JOIN order_details od ON o.OrderID = od.OrderID
                    JOIN product p ON od.ProductID = p.ProductID
                    WHERE o.OrderID = %s
                    GROUP BY o.OrderID
                """, (order_id,))

            db.commit()
            flash(f"✅ Pickup status updated to '{status}'.", "success")

        return redirect(url_for('order_management'))

    except Exception as e:
        db.rollback()
        flash(f"❌ Error updating pickup status: {e}", "danger")
        return redirect(url_for('order_management'))



# ---------------- ADMIN: DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if session.get('role_id') != 1:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor(dictionary=True) as cur:
            # Get total orders count
            cur.execute("SELECT COUNT(*) AS total_orders FROM `order`")
            total_order = cur.fetchone()["total_orders"]

            # Get order counts by status
            cur.execute("""
                SELECT Order_Status, COUNT(*) as count 
                FROM `order` 
                GROUP BY Order_Status
            """)
            # Initialize with only the statuses we want to show
            order_status_counts = {
                'Pending': 0,
                'Approved': 0,
                'Declined': 0
            }
            # Update with actual counts from the database
            for row in cur.fetchall():
                if row['Order_Status'] in order_status_counts:
                    order_status_counts[row['Order_Status']] = row['count']

            cur.execute("SELECT COUNT(*) AS total_transactions FROM transaction")
            total_transactions = cur.fetchone()["total_transactions"]

            # Get total stock count
            cur.execute("SELECT SUM(Stock) AS total_stock FROM product")
            stock_count = cur.fetchone()["total_stock"]

            # Get stock counts by category
            cur.execute("""
                SELECT 
                    c.Category_Name,
                    COALESCE(SUM(p.Stock), 0) as category_stock
                FROM category c
                LEFT JOIN product p ON c.CategoryID = p.CategoryID
                GROUP BY c.CategoryID, c.Category_Name
                ORDER BY c.Category_Name
            """)
            stock_by_category = {row['Category_Name']: row['category_stock'] for row in cur.fetchall()}

            # Get low stock products
            cur.execute("""
                SELECT p.Product_Name, p.Stock, c.Category_Name 
                FROM product p
                JOIN category c ON p.CategoryID = c.CategoryID
                WHERE p.Stock < 5
                ORDER BY p.Stock ASC
            """)
            low_stock = cur.fetchall()
            
            # Fetch pending orders with customer details
            cur.execute("""
                SELECT o.OrderID, o.Order_Date, 
                       CONCAT(u.F_Name, ' ', u.L_Name) as customer_name,
                       e.Email as customer_email,
                       (SELECT COUNT(*) FROM order_details WHERE OrderID = o.OrderID) as item_count,
                       (SELECT SUM(od.Quantity * p.Price) 
                        FROM order_details od 
                        JOIN product p ON od.ProductID = p.ProductID 
                        WHERE od.OrderID = o.OrderID) as total_amount
                FROM `order` o
                JOIN user u ON o.UserID = u.UserID
                JOIN email e ON u.UserID = e.UserID
                WHERE o.Order_Status = 'Pending'
                ORDER BY o.Order_Date DESC
                LIMIT 10
            """)
            pending_orders = cur.fetchall()

        # Sales over last 14 days
        with db.cursor(dictionary=True) as cur:
            cur.execute(
                """
                SELECT DATE(Transaction_Date) AS d, SUM(Total_Price) AS total
                FROM transaction
                GROUP BY DATE(Transaction_Date)
                ORDER BY d
                """
            )
            raw_sales = cur.fetchall() or []

        # Build a continuous date series for the last 14 days
        from datetime import datetime, timedelta
        today = datetime.now().date()
        start = today - timedelta(days=13)
        sales_map = {row['d']: float(row['total']) for row in raw_sales}
        labels = []
        values = []
        d = start
        while d <= today:
            labels.append(d.strftime('%b %d'))
            values.append(sales_map.get(d, 0.0))
            d += timedelta(days=1)

        return render_template(
            "dashboard.html",
            order_count=total_order,
            transaction_count=total_transactions,
            order_status_counts=order_status_counts,
            pending_orders=pending_orders,
            stock_count=stock_count,
            stock_by_category=stock_by_category,
            low_stock=low_stock,
            sales_labels=labels,
            sales_values=values,
        )
    except Exception as e:
        flash(f"Dashboard error: {e}", "danger")
        return render_template("dashboard.html")


# ---------------- ADMIN: MANAGE PRODUCTS ----------------

@app.route('/manage_products')
def manage_products():
    if session.get('role_id') != 1:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT ProductID AS id, Product_Name AS name, Description AS description,
                       Price AS price, Stock AS stock, CategoryID AS category, Image_url AS image_url
                FROM product
                ORDER BY ProductID DESC
            """)
            products = cur.fetchall()

        return render_template('manage_products.html', products=products)

    except Exception as e:
        flash(f"Could not load products: {e}", "danger")
        return render_template('manage_products.html', products=[])


# ---------------- ADMIN: ADD PRODUCT ----------------

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if session.get('role_id') != 1:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']
        image_url = request.form['image_url']

        try:
            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO product (Product_Name, Description, Price, Stock, CategoryID, Image_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, description, price, stock, category, image_url))
                db.commit()
            flash("✅ Product added successfully!", "success")
            return redirect(url_for('manage_products'))

        except Exception as e:
            db.rollback()
            flash(f"❌ Error adding product: {e}", "danger")

    return render_template('add_product.html')


# ---------------- ADMIN: EDIT PRODUCT ----------------

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if session.get('role_id') != 1:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT ProductID AS id, Product_Name AS name, Description AS description,
                       Price AS price, Stock AS stock, CategoryID AS category, Image_url AS image_url
                FROM product
                WHERE ProductID = %s
            """, (product_id,))
            product = cur.fetchone()

        if not product:
            flash("Product not found.", "warning")
            return redirect(url_for('manage_products'))

        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = request.form['price']
            stock = request.form['stock']
            category = request.form['category']
            image_url = request.form['image_url']

            with db.cursor() as cur:
                cur.execute("""
                    UPDATE product
                    SET Product_Name=%s, Description=%s, Price=%s, Stock=%s, CategoryID=%s, Image_url=%s
                    WHERE ProductID=%s
                """, (name, description, price, stock, category, image_url, product_id))
                db.commit()

            flash("✅ Product updated successfully!", "success")
            return redirect(url_for('manage_products'))

        return render_template('edit_product.html', product=product)

    except Exception as e:
        db.rollback()
        flash(f"❌ Error editing product: {e}", "danger")
        return redirect(url_for('manage_products'))


# ---------------- ADMIN: DELETE PRODUCT ----------------

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if session.get('role_id') != 1:
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor() as cur:
            cur.execute("DELETE FROM product WHERE ProductID=%s", (product_id,))
            db.commit()
        flash("🗑️ Product deleted successfully!", "success")

    except Exception as e:
        db.rollback()
        flash(f"❌ Error deleting product: {e}", "danger")

    return redirect(url_for('manage_products'))


# ---------------- ADMIN: TRANSACTIONS PAGE ----------------

@app.route('/transactions')
@login_required
def transactions_page():
    if session.get('role_id') not in [1, 3]:  # Allow both admin (1) and employee (3)
        flash("Access denied. Admins and employees only.", "danger")
        return redirect(url_for('login'))

    try:
        with db.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT t.TransactionID, t.Transaction_Date, t.OrderID,
                       CONCAT(u.F_Name, ' ', u.L_Name) AS customer,
                       t.Total_Price
                FROM transaction t
                JOIN `order` o ON t.OrderID = o.OrderID
                JOIN user u ON o.UserID = u.UserID
                ORDER BY t.Transaction_Date DESC
            """)
            transactions = cur.fetchall()

        # Format dates if needed (optional)
        for tx in transactions:
            if isinstance(tx["Transaction_Date"], datetime):
                tx["Transaction_Date"] = tx["Transaction_Date"].strftime("%Y-%m-%d")

        return render_template("transactions.html", transactions=[
            {
                "id": tx["TransactionID"],
                "date": tx["Transaction_Date"],
                "order_id": tx["OrderID"],
                "user": tx["customer"],
                "total": tx["Total_Price"]
            }
            for tx in transactions
        ])

    except Exception as e:
        flash(f"❌ Could not load transactions: {e}", "danger")
        return render_template("transactions.html", transactions=[])





if __name__ == '__main__':
    print("✅ Flask app running! Visit http://127.0.0.1:5000/")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)