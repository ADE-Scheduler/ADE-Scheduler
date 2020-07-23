from flask_assets import Bundle


bundles = {
    # Template
    'base_css': Bundle(
        'css/base.css',
        'css/lib/bootstrap.min.css',
        output='gen/base.min.css', filters='cssmin'),
    'base_js': Bundle(
        'js/lib/vue.dev.js',
        'js/lib/axios.min.js',
        'js/lib/bootstrap.bundle.min.js',
        'js/base.js',
        output='gen/base.min.js', filters='jsmin'),

    # Calendar
    'calendar_css': Bundle(
        'lib/fullcalendar/main.css',
        'css/calendar.css',
        output='gen/calendar.min.css', filters='cssmin'),
    'calendar_js': Bundle(
        'lib/fullcalendar/main.js',
        'js/calendar.js',
        output='gen/calendar.min.js', filters='jsmin'),

    # Account
    'account_css': Bundle(
        'components/vue-swatches/vue-swatches.min.css',
        'css/account.css',
        output='gen/account.min.css', filters='cssmin'),
    'account_js': Bundle(
        'components/vue-swatches/vue-swatches.min.js',
        'js/account.js',
        output='gen/account.min.js', filters='jsmin'),
}
