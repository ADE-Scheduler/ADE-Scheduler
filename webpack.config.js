const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = {
    mode: 'development',
    entry: {
        welcome: './static/js/welcome.js',
        calendar: './static/js/calendar.js',
        account: './static/js/account.js',
        classroom: './static/js/classroom.js',
        help: './static/js/help.js',
        change_password: './static/js/security/change_password.js',
        forgot_password: './static/js/security/forgot_password.js',
        login_user: './static/js/security/login_user.js',
        register_user: './static/js/security/register_user.js',
        reset_password: './static/js/security/reset_password.js',
    },
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.esm.js'
        }
    },
    module: {
        rules: [
            {
                test: /\.(png|jpe?g|gif|svg)$/,
                use: [{
                    loader: 'file-loader',
                    options: {
                        name: '[name].[contenthash].[ext]',
                        outputPath: 'img',
                        esModule: false
                    }
                }]
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            },
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin()
    ],
    output: {
        path: __dirname + '/static/dist',
        filename: '[name].bundle.js',
        publicPath: '/static/dist/'
    },
}
