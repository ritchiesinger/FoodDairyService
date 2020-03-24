import React from 'react'
import {render} from 'react-dom'
import {BrowserRouter} from 'react-router-dom'
import App from './components/App/App.jsx'
import 'bootstrap/dist/css/bootstrap.min.css'
require('bootstrap')
import 'jquery'
import 'popper.js'
render(<BrowserRouter><App/></BrowserRouter>, document.getElementById('App'))