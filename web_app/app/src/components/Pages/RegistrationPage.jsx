import React, {Component} from 'react'
import Page from 'pages/Page.jsx'
import {Redirect} from 'react-router-dom'
import {TextFieldInput, Button, Form} from 'common/Forms.jsx'
import {ErrorMessage} from 'common/Alerts.jsx'
import {registration} from 'api/api.jsx'

export default class RegistrationPage extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {registration: false},
      error: {errorCode: null, errorText: null},
      form: {login: '', password: '', confirmPassword: '', email: ''},
      registrationSuccess: false
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
    case 'confirmPassword':
      this.setState({...this.state,
        form: {...form, confirmPassword: event.currentTarget.value}})
      break
    case 'email':
      this.setState({...this.state,
        form: {...form, email: event.currentTarget.value}})
      break
    }
  }
  render() {
    const {props, state, handleSearchFormChange} = this
    const {form, error, loading, registrationSuccess} = state
    const {user} = props
    //console.log("Состояние формы авторизации:", state)
    if (user.login) {
      return <Redirect to={{pathname: "/admin/users"}}/>
    } else if (registrationSuccess) {
      return <Redirect to={{pathname: "/login"}}/>
    } else {
    return (
      <Page>
        <Form>
          <div className='col-12 col-sm-8 col-lg-6 offset-sm-2 offset-lg-3'><h3 className='text-center'>Регистрация</h3></div>
            <TextFieldInput id='login' header='Логин' value={form.login} isValid disabled={loading.registration}
              adaptiveClasses='col-12 col-sm-8 col-lg-6 offset-sm-2 offset-lg-3' action={() => {}} changeValue={handleSearchFormChange}/>
            <TextFieldInput id='password' header='Пароль' value={form.password} isValid disabled={loading.registration}
              adaptiveClasses='col-12 col-sm-8 col-lg-6 offset-sm-2 offset-lg-3' type='password' action={() => {}} changeValue={handleSearchFormChange}/>
            <TextFieldInput id='confirmPassword' header='Повторите пароль' type='password' value={form.confirmPassword} isValid disabled={loading.registration}
              adaptiveClasses='col-12 col-sm-8 col-lg-6 offset-sm-2 offset-lg-3' action={() => {}} changeValue={handleSearchFormChange}/>
            <TextFieldInput id='email' header='Email' value={form.email} type='email' isValid disabled={loading.registration}
              adaptiveClasses='col-12 col-sm-8 col-lg-6 offset-sm-2 offset-lg-3' action={() => {}} changeValue={handleSearchFormChange} />
            <div className='col-12 col-sm-8 col-md-4 col-lg-3 col-xl-2 offset-sm-2 offset-lg-3 align-self-end' style={{marginBottom: '1.45rem'}}>
              <Button btnBlock loading={loading.registration} loadingText='Загрузка' action={()=>{registration(form, this)}}>Отправить</Button>
            </div>
        </Form>
        {error.errorText ? <ErrorMessage>{error.errorText}</ErrorMessage> : null}
      </Page>)
    }
  }
}