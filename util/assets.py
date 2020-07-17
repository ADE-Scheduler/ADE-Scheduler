from flask_assets import Bundle


bundles = {
    # Template
    'base_css': Bundle(
        'css/base.css',
        'css/lib/bootstrap.min.css',
        output='gen/base.min.css', filters='cssmin'),
    'base_js': Bundle(
        'js/lib/jquery.min.js',
        'js/lib/bootstrap.bundle.min.js',
        'js/base.js',
        output='gen/base.min.js', filters='jsmin'),

    # Calendar
    'calendar_css': Bundle(
        'css/calendar.css',
        'lib/fullcalendar/core/main.css',
        'lib/fullcalendar/daygrid/main.css',
        'lib/fullcalendar/timegrid/main.css',
        'lib/fullcalendar/list/main.css',
        output='gen/calendar.min.css', filters='cssmin'),
    'calendar_js': Bundle(
        'js/calendar.js',
        'lib/fullcalendar/core/main.js',
        'lib/fullcalendar/interaction/main.js',
        'lib/fullcalendar/daygrid/main.js',
        'lib/fullcalendar/list/main.js',
        'lib/fullcalendar/timegrid/main.js',
        'lib/fullcalendar/bootstrap/main.js',
        'lib/fullcalendar/core/locales/fr.js',
        output='gen/calendar.min.js', filters='jsmin'),

    # Account
    'account_css': Bundle(
        'css/account.css',
        output='gen/account.min.css', filters='cssmin'),
    'account_js': Bundle(
        'js/account.js',
        output='gen/account.min.js', filters='jsmin'),
}
