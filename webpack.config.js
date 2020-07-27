module.exports = {
    mode: 'development',
    entry: {
        calendar: "./static/js/calendar.js",
        account: "./static/js/account.js",
        classroom: "./static/js/classroom.js",
        help: "./static/js/help.js",
        change_password: "./static/js/security/change_password.js",
        forgot_password: "./static/js/security/forgot_password.js",
        login_user: "./static/js/security/login_user.js",
        register_user: "./static/js/security/register_user.js",
        reset_password: "./static/js/security/reset_password.js",
    },
    devtool: 'inline-source-map',
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js'
        }
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    },
    output: {
        path: __dirname + "/static/dist",
        filename: "[name].bundle.js"
    },
}
