import React, {Component} from 'react'
import {Switch, Route, withRouter} from 'react-router-dom'
import Header from '../Header/Header.jsx'
import Footer from '../Footer/Footer.jsx'
import Page from 'pages/Page.jsx'
import AuthPage from 'pages/AuthPage.jsx'
import RegistrationPage from 'pages/RegistrationPage.jsx'
import Guest from 'pages/Guest.jsx'
import {ErrorMessage} from 'common/Alerts.jsx'
import AdminUsersPage from 'pages/AdminPages/Users.jsx'
import {getTokens, getMyProfile} from 'api/api.jsx'
import Cookies from 'universal-cookie'

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {login: false},
      error: {errorText: null, errorCode: null},
      user: {
        login: '',
        email: '',
        roles: [],
        logout_action: null
      }
    }
  }
  componentDidMount = () => {
    $('body').tooltip({selector: '[data-toggle="tooltip"], [title]:not([data-toggle="popover"])', trigger: 'hover', container: 'body'}
    ).on('click mousedown mouseup', '[data-toggle="tooltip"], [title]:not([data-toggle="popover"])', function () {
      $('[data-toggle="tooltip"], [title]:not([data-toggle="popover"])').tooltip('dispose')})
    const cookies = new Cookies()
    const allCookies = cookies.getAll()
    if (allCookies.AuthToken || allCookies.RefreshToken) {
      getMyProfile({username: allCookies.AuthToken, password: allCookies.RefreshToken}, this)
    }
  }
  login = auth => {
    getTokens(auth, this)
  }
  logout = () => {
    const cookies = new Cookies()
    cookies.remove("AuthToken")
    cookies.remove('RefreshToken')
    console.log('Установлены cookies:', cookies.getAll())
    this.setState({...this.state, user: {login: '', email: '', roles: []}})
  }
  render() {
    const {state, login, logout} = this
    const {loading, error} = state
    const user = {...this.state.user, logout_action: this.logout}
    return (
      <div id='app'>
        <Header logout={logout} user={user}/>
        <Switch>
          <Route exact path={'/'} render={props => <Guest {...props}/>}/>
          <Route exact path={'/admin/users'} render={props => <AdminUsersPage {...props} user={user}/>}/>
          <Route exact path={'/login'} render={props => <AuthPage {...props} user={user} login={login} loginLoading={loading.login} loginError={error}/>}/>
          <Route exact path={'/registration'} render={props => <RegistrationPage {...props} user={user}/>}/>
          <Route component={() => <Page><ErrorMessage>Страница не найдена!</ErrorMessage></Page>} />
        </Switch>
        <Footer />
      </div>
    )
  }
}
export default withRouter(App)