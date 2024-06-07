
from flask import render_template, redirect, url_for, request, jsonify
from flask import current_app as app
from application.models import Admin, User, Category, Product, Order, OrderItem, Cart
from application.forms import RegistrationForm, LoginForm, AdminForm
from .database import db
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from datetime import datetime





@app.route("/")
def index():
    return render_template("index.html")


@app.route("/user")
def user():
    return render_template("user/user.html")

@app.route("/home", methods=['GET', 'POST'])
def home():
    categories = Category.query.all()

    if request.method == 'POST':
        search_term = request.form.get('search_term')

        # Check if the search term matches any category
        category = Category.query.filter(Category.category_name.ilike(f'%{search_term}%')).first()

        if category:
            # Retrieve the products under the matched category
            products = Product.query.filter(Product.category_id == category.category_id).all()
        else:
            # Retrieve the products based on the search term
            products = Product.query.filter(
                (Product.product_name.ilike(f'%{search_term}%'))  |
                (Product.price.ilike(f'%{search_term}%'))
            ).all()

        return render_template('user/search_results.html', products=products, categories=categories)

    # If it's a GET request or no search term provided, display all products
    products = Product.query.all()
    return render_template("user/home.html", title='HOME', products=products, categories=categories, username=current_user.username)





@app.route('/admin_home', methods=['GET', 'POST'])
def admin_home():
    #Adding categories
    category_name = request.args.get('categoryName')
    if category_name:
        category = Category(category_name=category_name)
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            pass

    categories = Category.query.all()
    if request.method == 'POST':
        search_term = request.form.get('search_term')

        # Check if the search term matches any category
        category = Category.query.filter(Category.category_name.ilike(f'%{search_term}%')).first()

        if category:
            # Retrieve the products under the matched category
            products = Product.query.filter(Product.category_id == category.category_id).all()
        else:
            # Retrieve the products based on the search term
            products = Product.query.filter(
                (Product.product_name.ilike(f'%{search_term}%'))  |
                (Product.price.ilike(f'%{search_term}%'))
            ).all()

        return render_template('admin/admin_search.html', products=products, categories=categories)


    return render_template('admin/admin_home.html', categories=categories)


# Update a category
@app.route('/categories/<int:category_id>/update', methods=['GET', 'POST'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        # Retrieve form data and update the category
        category.category_name = request.form['category_name']
        db.session.commit()

        # if(Category updated successfully)
        return redirect(url_for('admin_home'))

    return render_template('admin/update_category.html', category=category)


@app.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        db.session.delete(category)
        db.session.commit()
        #if(Category deleted successfully)
        return redirect(url_for('admin_home'))

    return redirect(url_for('admin_home'))





login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(user_id):
    # Load the user object from the database based on the admin_id
    return Admin.query.get(user_id)



@app.route("/admin", methods=['GET', 'POST'])
def admin():
    form = AdminForm()
    if form.validate_on_submit():
        username = form.admin_username.data
        password = form.admin_password.data

        # Authenticate the user
        user = Admin.query.filter_by(username=username).first()

        if not user:
            return jsonify(message='User not found'), 404

        if user.password != password:
            return jsonify(message='Invalid password'), 401

        # Log in the user
        login_user(user)
        return redirect(url_for('admin_home'))

    return render_template('admin/admin_login.html', title='Admin', form=form)



@login_manager.user_loader
def load_user(user_id):
    # Load the user object from the database based on the admin_id
    return User.query.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()   
    if form.validate_on_submit():
    # Check if user exists
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            return jsonify(message='User not found'), 404

        # Validate password
        if user.password != form.password.data:
            return jsonify(message='Invalid password'), 401
        
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('home'))

    return render_template('user/login.html', title='LOGIN', form=form)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()   
    if form.validate_on_submit():

        # Check if user already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            return jsonify(message='Username already exists'), 400

        # Create a new user
        new_user = User(username=form.username.data, password=form.password.data, address=form.address.data, phone_number=form.phone_num.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('user/register.html', title='REGISTER', form=form)






# Display products in a category
@app.route('/categories/<int:category_id>', methods=['GET'])
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    return render_template('admin/category.html', category=category)

#add product
@app.route('/categories/<int:category_id>/add_product', methods=['GET', 'POST'])
def add_product(category_id):
    category = Category.query.get_or_404(category_id)

    if request.method == 'POST':
        # Retrieve form data and create a new product
        product_name = request.form['product_name']
        price = request.form['price']
        image_url = request.form['image_url']
        quantity=request.form['quantity']

        product = Product(product_name=product_name, price=price, image_url=image_url,quantity=quantity, category=category)
        db.session.add(product)
        db.session.commit()

        #if(Product added successfully)
        return redirect(url_for('show_category', category_id=category_id))

    return render_template('admin/add_product.html', category=category)



# Update a product
@app.route('/products/<int:product_id>/update', methods=['GET', 'POST'])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    category_id = product.category_id

    if request.method == 'POST':
        # Retrieve form data and update the product
        product.product_name = request.form['product_name']
        product.price = request.form['price']
        product.image_url = request.form['image_url']
        product.quantity = request.form['quantity']

        db.session.commit()
        #if(Product updated successfully)
        return redirect(url_for('show_category', category_id=category_id))

    return render_template('admin/update_product.html', product=product)

# Delete a product
@app.route('/products/<int:product_id>/delete', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    category_id = product.category_id

    db.session.delete(product)
    db.session.commit()
    #if(Product deleted successfully)

    return redirect(url_for('show_category', category_id=category_id))



@app.route('/products/<int:product_id>/buy', methods=['GET', 'POST'])
def buy_product(product_id):
    # Get the product details based on the product_id
    product = Product.query.get_or_404(product_id)
    

    if request.method == 'POST':
        # Get the quantity entered by the user
        quantity = int(request.form['quantity'])

        if quantity > product.quantity:
            # If the requested quantity exceeds the available quantity, display an error message
            error_message = 'Insufficient quantity available.'
            return render_template('user/purchase.html', product=product, error_message=error_message)

        # Calculate the total amount
        total_amount = product.price * quantity

        order_date = datetime.now()

        # Logic for completing the purchase with the specified quantity
        # Calculate the total amount
        total_amount = product.price * quantity

        # Create an order
        order = Order(user_id=current_user.user_id, order_date=order_date, total_amount=total_amount)
        # Provide the total_amount
        db.session.add(order)
        db.session.commit()

        # Create an order item for the product
        order_item = OrderItem(order_id=order.order_id, product_id=product.product_id, quantity=quantity, price_per_item=product.price)
        db.session.add(order_item)

        # Update the product quantity
        product.quantity -= quantity
        db.session.commit()

        # Render the purchase confirmation template with the total amount
        return render_template('user/purchase_confirmation.html',order=order,order_item=order_item, product=product, quantity=quantity, total_amount=total_amount)

    # Render the buy form template for the user to enter the quantity
    return render_template('user/buy_form.html', product=product,)



@app.route('/products/<int:product_id>/add_to_cart', methods=['GET'])
@login_required  # Require the user to be logged in
def add_to_cart(product_id):
    # Find the product in the database
    product = Product.query.get(product_id)
    quantity=0
    if product.quantity>0:
        # Create a new cart item for the user
        #if product in current_user.cart_item:
         #       cart_item = Cart(user_id=current)
        cart_item = Cart(user_id=current_user.user_id, product_id=product_id, quantity=quantity+1)
        db.session.add(cart_item)
        db.session.commit()
        
        
    
    return redirect(url_for('home'))


def calculate_cart_total():
    total = 0
    for cart_item in current_user.cart_items:
        total += cart_item.product.price * cart_item.quantity
    return total


@app.route('/cart', methods=['GET'])
def cart():
    # Logic for fetching the cart items and rendering the cart template
    cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()
    return render_template('user/cart.html', cart_items=cart_items, total=calculate_cart_total())

@app.route('/cart/remove/<int:cart_item_id>', methods=['GET'])
def remove_from_cart(cart_item_id):
    # Logic for removing the item from the cart
    cart_item = Cart.query.get_or_404(cart_item_id)

    db.session.delete(cart_item)
    db.session.commit()

    return redirect(url_for('cart'))


@app.route('/cart/checkout', methods=['GET'])
def checkout():
    # Get all the cart items for the current user
    cart_items = Cart.query.filter_by(user_id=current_user.user_id).all()

    # Calculate the total amount
    total_amount = sum(cart_item.product.price * cart_item.quantity for cart_item in cart_items)

    # Create an order for the current user with the total amount
    order = Order(user_id=current_user.user_id, order_date=datetime.utcnow(), total_amount=total_amount)
    db.session.add(order)
    db.session.commit()

    # Move cart items to order items and update the product quantity
    for cart_item in cart_items:
        product = Product.query.get(cart_item.product_id)
        if product.quantity < cart_item.quantity:
            # If the requested quantity exceeds the available quantity
            return redirect(url_for('cart'))

        # Create an order item for the product
        order_item = OrderItem(
            order_id=order.order_id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price_per_item=product.price
        )

        # Update the product quantity
        product.quantity -= cart_item.quantity

        db.session.add(order_item)
        db.session.delete(cart_item)

    db.session.commit()

    #if(order has been placed successfully)
    return redirect(url_for('order_confirmation', order_id=order.order_id))

@app.route('/order_confirmation/<int:order_id>', methods=['GET'])
def order_confirmation(order_id):
    # Fetch the order and associated order items
    order = Order.query.get_or_404(order_id)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()

    # Fetch the product information for each order item
    for order_item in order_items:
        order_item.product = Product.query.get(order_item.product_id)

    return render_template('user/order_confirmation.html', order=order, order_items=order_items)




@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()


