from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify, g
from adminapp import app
import sqlite3
from flask import Blueprint, abort

DATABASE = "database.sqlite"
admin = Blueprint('admin', __name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


# Trang chủ
@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'admin_dashboard.html',
        title='Trang chủ',
        year=datetime.now().year,
    )


# Xác thực admin
def admin_required():
    if 'admin' not in session:
        flash("Bạn cần đăng nhập với tư cách admin!", "danger")
        return redirect(url_for("admin_login"))

# Trang đăng nhập admin
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':  # Thay bằng xác thực database nếu cần
            session['admin'] = True
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash("Sai tài khoản hoặc mật khẩu", "danger")

    return render_template('admin/login.html')

# Đăng xuất admin
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for('admin_login'))

# Trang quản lý admin
@admin.route('/')
def admin_dashboard():
    admin_required()
    return render_template(
        'admin/dashboard.html',
        title='Bảng Điều Khiển Admin',
        year=datetime.now().year
    )

# Quản lý đơn hàng
@admin.route('/orders')
def admin_orders():
    admin_required()
    db = get_db()
    orders = db.execute("SELECT * FROM orders").fetchall()
    
    return render_template(
        'admin/orders.html',
        title='Quản lý Đơn Hàng',
        year=datetime.now().year,
        orders=orders
    )

# Theo dõi đơn hàng theo ID
@admin.route('/track_order', methods=['GET'])
def admin_track_order():
    admin_required()
    order_id = request.args.get("order_id")
    order = None
    if order_id:
        db = get_db()
        cur = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cur.fetchone()
    
    return render_template("admin/track_order.html", order=order)

# Quản lý xe tự hành
@admin.route('/vehicles')
def admin_vehicles():
    admin_required()
    return render_template(
        'admin/vehicles.html',
        title='Quản lý Xe Tự Hành',
        year=datetime.now().year
    )

# Route hiển thị trang web tracking
@app.route('/tracking')
def tracking():
    return render_template('admin_tracking.html')

# API giả lập vị trí GPS
@app.route('/get_location')
def get_location():
    lat = 10.7769 + random.uniform(-0.005, 0.005)  # Vị trí thay đổi giả lập
    lon = 106.7009 + random.uniform(-0.005, 0.005)
    return jsonify({'lat': lat, 'lon': lon})


# API kiểm tra trạng thái đơn hàng (để cập nhật trên bản đồ thời gian thực)
@admin.route('/api/order_status/<order_id>')
def admin_order_status(order_id):
    admin_required()
    status = {
        "order_id": order_id,
        "status": "Đang giao hàng",
        "location": "Quận 1, TP.HCM"
    }
    return jsonify(status)

# Đăng ký blueprint admin
app.register_blueprint(admin, url_prefix='/admin')
