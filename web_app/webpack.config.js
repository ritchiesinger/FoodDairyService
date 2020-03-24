const webpack = require('webpack');
const path = require('path');

module.exports = {
    plugins: [
        new webpack.ProvidePlugin({
          $: 'jquery',
          jQuery: 'jquery',
          'window.jQuery': 'jquery'
        })
    ],
    devServer: {
        contentBase: path.join(__dirname, 'dist'),
        port: 9000,
        index: 'index.html',
        historyApiFallback: true
    },
    entry: './app/src/index.jsx',
    output: {
        filename: 'index.js',
        path: path.resolve(__dirname, '../service/static')
    },
    mode: 'development',
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: [
                    'babel-loader',
                    'eslint-loader',
                ],
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            },
            {
                test: /\.(png|svg|jpg|gif)$/,
                loader: 'file-loader',
                options: {
                    outputPath: 'images',
                  },
            },
            {
                test: /\.(woff(2)?|ttf|eot)(\?v=\d+\.\d+\.\d+)?$/,
                use: [{
                    loader: 'file-loader',
                    options: {
                        name: '[name].[ext]',
                        outputPath: 'fonts/'
                    }
                }]
            },
            {
                test: /\.jsx?$/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env', '@babel/preset-react'],
                        exclude: /(node_modules)/,
                        plugins: [
                            // Stage 0
                            '@babel/plugin-proposal-function-bind',
                            // Stage 1
                            '@babel/plugin-proposal-export-default-from',
                            '@babel/plugin-proposal-logical-assignment-operators',
                            ['@babel/plugin-proposal-optional-chaining', { loose: false }],
                            ['@babel/plugin-proposal-pipeline-operator', { proposal: 'minimal' }],
                            ['@babel/plugin-proposal-nullish-coalescing-operator', { loose: false }],
                            '@babel/plugin-proposal-do-expressions',
                            // Stage 2
                            ['@babel/plugin-proposal-decorators', { legacy: true }],
                            '@babel/plugin-proposal-function-sent',
                            '@babel/plugin-proposal-export-namespace-from',
                            '@babel/plugin-proposal-numeric-separator',
                            '@babel/plugin-proposal-throw-expressions',
                            // Stage 3
                            '@babel/plugin-syntax-dynamic-import',
                            '@babel/plugin-syntax-import-meta',
                            ['@babel/plugin-proposal-class-properties', { loose: false }],
                            '@babel/plugin-proposal-json-strings'
                        ]
                    }
                }
            }
        ]
    },
    resolve: {
        alias: {
          common: path.resolve(__dirname, 'app/src/components/Common'),
          pages: path.resolve(__dirname, 'app/src/components/Pages'),
          api: path.resolve(__dirname, 'app/src/api'),
          assets: path.resolve(__dirname, 'app/assets')
        }
    }
};