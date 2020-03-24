import React, {Component} from 'react'
import Page from 'pages/Page.jsx'
import {Redirect} from 'react-router-dom'
import {TextFieldInput, Button, LinkButton, Form} from 'common/Forms.jsx'
import {ErrorMessage} from 'common/Alerts.jsx'

export default class AuthPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      error: {errorCode: null, errorText: null},
      form: {login: '', password: ''}
    }
  }
  handleSearchFormChange = (event) => {
    const {form} = this.state
    switch (event.currentTarget.id) {
    case 'login':
      this.setState({...this.state,
        form: {...form, login: event.currentTarget.value}})
      break
    case 'password':
      this.setState({...this.state,
        form: {...form, password: event.currentTarget.value}})
      break
    }
  }
  render() {
    const {props, state, handleSearchFormChange} = this
    const {form, error} = state
    const {login, user, loginLoading, loginError} = props
    return user.login ? <Redirect to={{pathname: "/admin/users"}}/> : (
      <Page>
        <Form>
            <div className='col-12 col-sm-8 col-lg-6 offset-sm-2 offset-lg-3'><h3 className='text-center'>Авторизация</h3></div>
            <TextFieldInput id='login' header='Логин' value={form.login} isValid disabled={loginLoading}
            adaptiveClasses='col-12 col-sm-8 col-lg-6 offset-sm-2 offset-lg-3' action={() => {}} changeValue={handleSearchFormChange} />
            <TextFieldInput id='password' header='Пароль' value={form.password} isValid disabled={loginLoading} type='password'
            adaptiveClasses='col-12 col-sm-8 col-lg-6 offset-sm-2 offset-lg-3' action={() => {}} changeValue={handleSearchFormChange} />
            <div className='col-12 col-sm-8 col-md-4 col-lg-3 col-xl-2 offset-sm-2 offset-lg-3 align-self-end' style={{marginBottom: '1.45rem'}}>
                <Button btnBlock loading={loginLoading} loadingText='Загрузка' action={()=>{login({username: form.login, password: form.password})}}>Войти</Button>
            </div>
            {loginError.errorText ? <div className='col-12 col-sm-8 col-lg-6 offset-sm-2 offset-lg-3'><ErrorMessage>{loginError.errorText}</ErrorMessage></div> : null}
        </Form>
      </Page>
    )
  }
}