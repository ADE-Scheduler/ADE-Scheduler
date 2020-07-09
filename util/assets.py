from flask_assets import Bundle


bundles = {
    # Template
    'base_css': Bundle(
        'css/lib/bootstrap.min.css',
        'css/base.css',
        'lib/fontawesome/css/all.min.css',
        'img/favicon.ico',
        output='gen/base.css', filters='cssmin'),
    'base_js': Bundle(
        'js/lib/jquery.min.js',
        'js/lib/popper.min.js',
        'js/lib/bootstrap.min.js',
        'js/base.js',
        output='gen/base.js', filters='jsmin'),

    # Calendar
    'calendar_css': Bundle(
        'css/calendar.css',
        'lib/fullcalendar/core/main.css',
        'lib/fullcalendar/daygrid/main.css',
        'lib/fullcalendar/timegrid/main.css',
        'lib/fullcalendar/list/main.css',
        output='gen/calendar.css', filters='cssmin'),
    'calendar_js': Bundle(
        'js/calendar.js',
        'lib/fullcalendar/core/main.js',
        'lib/fullcalendar/interaction/main.js',
        'lib/fullcalendar/daygrid/main.js',
        'lib/fullcalendar/list/main.js',
        'lib/fullcalendar/timegrid/main.js',
        'lib/fullcalendar/bootstrap/main.js',
        'lib/fullcalendar/core/locales/fr.js',
        output='gen/calendar.js', filters='jsmin'),
}
