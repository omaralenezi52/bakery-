import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime, timedelta
import random
import os

# إعداد مسارات المجلدات لضمان عملها على السيرفر (Render)
base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')
db_path = os.path.join(base_dir, 'database.db')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'bakery_legendary_key_2026'

def get_db_connection():
    # استخدام المسار المطلق لقاعدة البيانات
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # جدول المنتجات
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            cost REAL NOT NULL DEFAULT 0,
            image_url TEXT NOT NULL,
            category TEXT DEFAULT 'عام',
            badge TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول المبيعات
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # إضافة منتجات افتراضية إذا كانت القاعدة فارغة
    check = conn.execute('SELECT count(*) FROM products').fetchone()
    if check[0] == 0:
        products_data = [
            ('كيكة الفانيلا الملكية', 'كيكة طرية مغطاة بكريمة الزبدة الفرنسية مع رشّ اللوز المحمّص', 75.0, 30.0, 'https://images.unsplash.com/photo-1550617931-e17a7b70dce2?q=80&w=500', 'كيكات', 'الأكثر مبيعاً'),
            ('كب كيك الشوكولاتة الداكنة', 'كب كيك بعجينة شوكولاتة بلجيكية 70% مع طبقة غاناش ناعمة', 25.0, 10.0, 'https://images.unsplash.com/photo-1599785209707-a456fc1337bb?q=80&w=500', 'كب كيك', 'جديد'),
            ('تارت الفراولة الفرنسي', 'قاعدة هشة من المعجنات الفرنسية مع كريمة باتيسيير وفراولة طازجة', 55.0, 22.0, 'https://images.unsplash.com/photo-1488477181946-6428a0291777?q=80&w=500', 'تارت', ''),
            ('مافن التوت البري', 'مافن بالتوت البري الطازج مع قشرة ليمون وسكر الكاسترد', 18.0, 7.0, 'https://images.unsplash.com/photo-1558303910-41f6b7b96ead?q=80&w=500', 'مافن', 'مميز'),
            ('كيكة الشوكولاتة الألمانية', 'طبقات من كيكة الشوكولاتة مع كريمة جوز الهند والكاراميل', 95.0, 40.0, 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?q=80&w=500', 'كيكات', 'حصري'),
            ('مكرون الفستق الأخضر', 'مكرون فرنسي بالفستق الحلبي مع حشوة ناعمة من كريمة الفستق', 15.0, 5.0, 'https://images.unsplash.com/photo-1569864358642-9d1684040f43?q=80&w=500', 'مكرون', ''),
            ('رول القرفة الأمريكي', 'رول طازج من عجينة البريوش مع حشوة القرفة والزبيب وتغليف الكريمة', 20.0, 8.0, 'https://images.unsplash.com/photo-1609428651985-f9abb43ea6e0?q=80&w=500', 'مخبوزات', 'الأكثر طلباً'),
            ('تشيز كيك نيويورك', 'تشيز كيك كريمي بالطريقة الأصيلة مع صلصة التوت الأحمر', 65.0, 28.0, 'https://images.unsplash.com/photo-1508737027454-e6454ef45afd?q=80&w=500', 'كيكات', ''),
        ]
        conn.executemany('INSERT INTO products (title, description, price, cost, image_url, category, badge) VALUES (?, ?, ?, ?, ?, ?, ?)', products_data)
        
        # إنشاء بيانات مبيعات وهمية للـ 30 يوم الماضية
        product_ids = [row[0] for row in conn.execute('SELECT id FROM products').fetchall()]
        
        for days_ago in range(30, 0, -1):
            sale_date = datetime.now() - timedelta(days=days_ago)
            daily_sales = random.randint(3, 15)
            for _ in range(daily_sales):
                product_id = random.choice(product_ids)
                product_row = conn.execute('SELECT price FROM products WHERE id=?', (product_id,)).fetchone()
                quantity = random.randint(1, 4)
                unit_price = product_row['price']
                total_price = unit_price * quantity
                conn.execute(
                    'INSERT INTO sales (product_id, quantity, unit_price, total_price, sale_date) VALUES (?, ?, ?, ?, ?)',
                    (product_id, quantity, unit_price, total_price, sale_date.strftime('%Y-%m-%d %H:%M:%S'))
                )
    
    conn.commit()
    conn.close()

# تهيئة قاعدة البيانات عند بدء التشغيل
init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== المسارات (Routes) =====

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products, categories=categories)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
    if not product:
        conn.close()
        return redirect(url_for('index'))
    
    related = conn.execute(
        'SELECT * FROM products WHERE category=? AND id!=? LIMIT 4',
        (product['category'], product_id)
    ).fetchall()
    
    stats = conn.execute(
        'SELECT SUM(quantity) as total_sold, COUNT(*) as orders FROM sales WHERE product_id=?',
        (product_id,)
    ).fetchone()
    conn.close()
    
    total_sold = stats['total_sold'] or 0
    orders = stats['orders'] or 0
    
    return render_template('product.html', product=product, related=related, total_sold=total_sold, orders=orders)

@app.route('/category/<cat>')
def category(cat):
    conn = get_db_connection()
    if cat == 'all':
        products = conn.execute('SELECT * FROM products').fetchall()
    else:
        products = conn.execute('SELECT * FROM products WHERE category=?', (cat,)).fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products, categories=categories, active_cat=cat)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '12345':
            session['logged_in'] = True
            flash('مرحباً بك في لوحة التحكم! 🎉', 'success')
            return redirect(url_for('admin'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    conn = get_db_connection()
    today = datetime.now().strftime('%Y-%m-%d')
    today_sales = conn.execute("SELECT COALESCE(SUM(total_price),0) as total, COUNT(*) as count FROM sales WHERE date(sale_date)=?", (today,)).fetchone()
    
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    week_sales = conn.execute("SELECT COALESCE(SUM(total_price),0) as total, COUNT(*) as count FROM sales WHERE date(sale_date)>=?", (week_ago,)).fetchone()
    
    month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    month_sales = conn.execute("SELECT COALESCE(SUM(total_price),0) as total, COUNT(*) as count FROM sales WHERE date(sale_date)>=?", (month_ago,)).fetchone()
    
    month_cost_row = conn.execute("""SELECT COALESCE(SUM(s.quantity * p.cost),0) as total_cost FROM sales s JOIN products p ON s.product_id=p.id WHERE date(s.sale_date)>=?""", (month_ago,)).fetchone()
    
    top_products = conn.execute("""SELECT p.title, p.image_url, p.price, p.category, SUM(s.quantity) as total_qty, SUM(s.total_price) as total_revenue FROM products p LEFT JOIN sales s ON p.id=s.product_id GROUP BY p.id ORDER BY total_qty DESC LIMIT 5""").fetchall()
    
    daily_chart = []
    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_label = (datetime.now() - timedelta(days=i)).strftime('%m/%d')
        row = conn.execute("SELECT COALESCE(SUM(total_price),0) as revenue FROM sales WHERE date(sale_date)=?", (day,)).fetchone()
        daily_chart.append({'day': day_label, 'revenue': round(row['revenue'], 2)})
    
    products = conn.execute('SELECT * FROM products ORDER BY created_at DESC').fetchall()
    total_products = conn.execute('SELECT COUNT(*) as c FROM products').fetchone()['c']
    conn.close()
    
    net_profit = round(month_sales['total'] - month_cost_row['total_cost'], 2)
    avg_daily = round(month_sales['total'] / 30, 2) if month_sales['total'] > 0 else 0
    avg_weekly = round(month_sales['total'] / 4, 2) if month_sales['total'] > 0 else 0
    
    return render_template('admin.html',
        today_revenue=round(today_sales['total'], 2), today_orders=today_sales['count'],
        week_revenue=round(week_sales['total'], 2), week_orders=week_sales['count'],
        month_revenue=round(month_sales['total'], 2), month_orders=month_sales['count'],
        month_cost=round(month_cost_row['total_cost'], 2), net_profit=net_profit,
        avg_daily=avg_daily, avg_weekly=avg_weekly, top_products=top_products,
        daily_chart=daily_chart, products=products, total_products=total_products
    )

@app.route('/admin/add', methods=['POST'])
@login_required
def add_product():
    title = request.form['title']
    description = request.form['description']
    price = float(request.form['price'])
    cost = float(request.form.get('cost', 0))
    image_url = request.form['image_url']
    category_val = request.form.get('category', 'عام')
    badge = request.form.get('badge', '')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO products (title, description, price, cost, image_url, category, badge) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (title, description, price, cost, image_url, category_val, badge))
    conn.commit()
    conn.close()
    flash(f'تم إضافة "{title}" بنجاح! 🎉', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id=?', (product_id,))
    conn.commit()
    conn.close()
    flash(f'تم حذف المنتج بنجاح', 'success')
    return redirect(url_for('admin'))

@app.route('/api/buy/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    conn = get_db_connection()
    product_row = conn.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
    if not product_row:
        conn.close()
        return jsonify({'error': 'منتج غير موجود'}), 404
    
    quantity = int(request.json.get('quantity', 1))
    total = product_row['price'] * quantity
    
    conn.execute('INSERT INTO sales (product_id, quantity, unit_price, total_price) VALUES (?, ?, ?, ?)',
                 (product_id, quantity, product_row['price'], total))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'تم إضافة المنتج للسلة! 🛒'})

@app.route('/api/chart-data')
@login_required
def chart_data():
    conn = get_db_connection()
    days = int(request.args.get('days', 7))
    data = []
    for i in range(days-1, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        label = (datetime.now() - timedelta(days=i)).strftime('%d/%m')
        row = conn.execute("SELECT COALESCE(SUM(total_price),0) as revenue, COUNT(*) as orders FROM sales WHERE date(sale_date)=?", (day,)).fetchone()
        data.append({'day': label, 'revenue': round(row['revenue'],2), 'orders': row['orders']})
    conn.close()
    return jsonify(data)

# تشغيل السيرفر مع ضبط البورت المتوافق مع Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
