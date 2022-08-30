/* global module */
/* global __dirname */

const VueLoaderPlugin = require('vue-loader/lib/plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const pages = [
  // Security pages are no longer required; we keep them just in case...
  // 'security/change_password',
  // 'security/forgot_password',
  // 'security/login_user',
  // 'security/register_user',
  // 'security/reset_password',
  // 'security/send_confirmation',
  'errorhandler/403',
  'errorhandler/404',
  'errorhandler/500',
  'account',
  'calendar',
  'classroom',
  'help',
  'contact',
  'whatisnew',
  'contribute',
  'admin',
];

const conf = {
  mode: 'development',
  entry: {},
  resolve: {
    alias: {
      vue$: 'vue/dist/vue.esm.js',
    },
  },
  module: {
    rules: [
      {
        test: /\.(png|jpe?g|gif|svg)$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[contenthash].[ext]',
              outputPath: 'img',
              esModule: false,
            },
          },
        ],
      },
      {
        test: /\.(sa|sc|c)ss$/,
        use: ['vue-style-loader', 'style-loader', 'css-loader', 'sass-loader'],
      },
      {
        test: /\.vue$/,
        loader: 'vue-loader',
      },
      {
        test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[name].[ext]',
              outputPath: 'fonts/',
            },
          },
        ],
      },
    ],
  },
  plugins: [
    new VueLoaderPlugin(),
    new HtmlWebpackPlugin({
      inject: false,
      minify: false,
      template: './templates/base.html',
      filename: './html/base.html',
    }),
    new HtmlWebpackPlugin({
      inject: false,
      minify: false,
      template: './templates/custom_macros.html',
      filename: './html/custom_macros.html',
    }),
  ],
  output: {
    path: `${__dirname}/static/dist/`,
    filename: '[name].bundle.js',
    publicPath: '/static/dist/',
  },
};

pages.forEach((page) => {
  const entryPath = `./static/js/${page}.js`;
  const entryName = page.split('/').pop();
  conf.entry[entryName] = entryPath;
  conf.plugins.push(
    new HtmlWebpackPlugin({
      hash: true,
      inject: false,
      minify: false,
      template: `./templates/${page}.html`,
      filename: `./html/${page}.html`,
      chunks: [entryName],
    })
  );
});

module.exports = conf;
