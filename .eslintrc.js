module.exports = {
	'env': {
		'browser': true,
		'es2021': true,
		'amd': true,
	},
	'extends': [
		'eslint:recommended',
		'plugin:vue/essential'
	],
	'parserOptions': {
		'ecmaVersion': 12,
		'sourceType': 'module'
	},
	'plugins': [
		'vue'
	],
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
