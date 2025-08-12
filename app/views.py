from app import app, db
from flask import render_template, request, redirect, url_for, flash, Response
import psutil
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .models import User
from .forms import UserForm


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

@app.route('/users')
def users():
    users = User.query.all()

    return render_template('users.html', users=users)

@app.route('/users/new', methods=['post', 'get'])
def new_user():
    new_user_form = UserForm()
    if new_user_form.validate_on_submit():
        username = new_user_form.username.data
        email = new_user_form.email.data
        password = new_user_form.password.data

        user = User(username, email, password)
        db.session.add(user)
        db.session.commit()

        flash('User successfully added!', 'success')
        redirect(url_for('users'))

    flash_errors(new_user_form)
    return render_template('add_user.html', form=new_user_form)


###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


@app.route('/metrics')
def metrics():
    """Expose system health metrics in Prometheus format."""
    # Collect system metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    vm = psutil.virtual_memory()
    du = psutil.disk_usage('/')
    
    # Create custom metrics
    from prometheus_client import Gauge
    
    # CPU usage
    cpu_gauge = Gauge('system_cpu_percent', 'CPU utilization percentage')
    cpu_gauge.set(cpu_percent)
    
    # Memory usage
    mem_total = Gauge('system_memory_total_bytes', 'Total system memory in bytes')
    mem_used = Gauge('system_memory_used_bytes', 'Used system memory in bytes')
    mem_free = Gauge('system_memory_free_bytes', 'Free system memory in bytes')
    mem_percent = Gauge('system_memory_used_percent', 'Memory utilization percentage')
    
    mem_total.set(vm.total)
    mem_used.set(vm.used)
    mem_free.set(vm.available)
    mem_percent.set(vm.percent)
    
    # Disk usage
    disk_total = Gauge('system_disk_total_bytes', 'Total disk size in bytes')
    disk_used = Gauge('system_disk_used_bytes', 'Used disk space in bytes')
    disk_free = Gauge('system_disk_free_bytes', 'Free disk space in bytes')
    disk_percent = Gauge('system_disk_used_percent', 'Disk utilization percentage')
    
    disk_total.set(du.total)
    disk_used.set(du.used)
    disk_free.set(du.free)
    disk_percent.set(du.percent)
    
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
