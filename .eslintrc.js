/* global module */

module.exports = {
  'env': {
    'browser': true,
    'es2021': true,
    'amd': true,
  },

  'extends': [
    'eslint:recommended',
    'plugin:vue/recommended',
  ],
  'parserOptions': {
    'ecmaVersion': 12,
    'sourceType': 'module'
  },
  'rules': {
    'indent': [
      'error',
      2
    ],
    'linebreak-style': [
      'error',
      'unix'
    ],
    'quotes': [
      'error',
      'single'
    ],
    'semi': [
      'error',
      'always'
    ]
  }
};
