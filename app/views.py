from app import app, db
from flask import render_template, request, redirect, url_for, flash, Response
from .models import User
from .forms import UserForm
import psutil


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


@app.route('/metrics')
def metrics():
    """Expose system health metrics in Prometheus format."""
    metrics_output = []

    # CPU metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count()
    metrics_output.append('# HELP system_cpu_usage_percent Current CPU usage percentage')
    metrics_output.append('# TYPE system_cpu_usage_percent gauge')
    metrics_output.append(f'system_cpu_usage_percent {cpu_percent}')
    metrics_output.append('# HELP system_cpu_count Number of CPUs')
    metrics_output.append('# TYPE system_cpu_count gauge')
    metrics_output.append(f'system_cpu_count {cpu_count}')

    # Memory metrics
    memory = psutil.virtual_memory()
    metrics_output.append('# HELP system_memory_total_bytes Total memory in bytes')
    metrics_output.append('# TYPE system_memory_total_bytes gauge')
    metrics_output.append(f'system_memory_total_bytes {memory.total}')
    metrics_output.append('# HELP system_memory_available_bytes Available memory in bytes')
    metrics_output.append('# TYPE system_memory_available_bytes gauge')
    metrics_output.append(f'system_memory_available_bytes {memory.available}')
    metrics_output.append('# HELP system_memory_used_bytes Used memory in bytes')
    metrics_output.append('# TYPE system_memory_used_bytes gauge')
    metrics_output.append(f'system_memory_used_bytes {memory.used}')
    metrics_output.append('# HELP system_memory_usage_percent Memory usage percentage')
    metrics_output.append('# TYPE system_memory_usage_percent gauge')
    metrics_output.append(f'system_memory_usage_percent {memory.percent}')

    # Disk metrics
    disk = psutil.disk_usage('/')
    metrics_output.append('# HELP system_disk_total_bytes Total disk space in bytes')
    metrics_output.append('# TYPE system_disk_total_bytes gauge')
    metrics_output.append(f'system_disk_total_bytes {disk.total}')
    metrics_output.append('# HELP system_disk_used_bytes Used disk space in bytes')
    metrics_output.append('# TYPE system_disk_used_bytes gauge')
    metrics_output.append(f'system_disk_used_bytes {disk.used}')
    metrics_output.append('# HELP system_disk_free_bytes Free disk space in bytes')
    metrics_output.append('# TYPE system_disk_free_bytes gauge')
    metrics_output.append(f'system_disk_free_bytes {disk.free}')
    metrics_output.append('# HELP system_disk_usage_percent Disk usage percentage')
    metrics_output.append('# TYPE system_disk_usage_percent gauge')
    metrics_output.append(f'system_disk_usage_percent {disk.percent}')

    return Response('\n'.join(metrics_output) + '\n', mimetype='text/plain; version=0.0.4; charset=utf-8')


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
