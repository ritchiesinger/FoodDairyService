import React, {Component} from 'react'
import Page from 'pages/Page.jsx'
import {Link, Redirect} from 'react-router-dom'
import queryString from 'query-string'
import {TextFieldInput, ListField, Button, LinkButton, DateTimeInput, Form} from 'common/Forms.jsx'
import Pagination from 'common/Pagination.jsx'
import {WarningMessage, SuccessMessage, ErrorMessage} from 'common/Alerts.jsx'
import {SearchPreloader, getSearchUrlFromObject} from 'common/Common.jsx'
import {searchUsers} from 'api/api.jsx'
import Cookies from 'universal-cookie'

const UsersSearchResultBlock = props => {
  const {usersList, loading} = props
  return (
    <div className='row position-relative'>
      {loading ? <div className='position-absolute' style={{top: 'calc(50% - 30px)', left: 'calc(50% - 50px)'}}><SearchPreloader /></div> : null}
      <div className='col' style={{opacity: loading ? '0.3' : '1', pointerEvents: loading ? 'none' : 'auto'}}>
        <div className='row d-none d-xl-flex pt-3 pb-3' style={{borderBottom: '1px solid rgba(0,0,0,.1)', borderTop: '1px solid rgba(0,0,0,.1)'}}>
          <div className='col-3 font-weight-bold'><span>Логин</span></div>
          <div className='col-3 font-weight-bold'><span>Email</span></div>
          <div className='col-3 font-weight-bold'><span>Роли</span></div>
          <div className='col-3 font-weight-bold'><span>Последняя активность</span></div>
        </div>
        <div className='subscription-row'>
          {usersList.map((user, index) => (
            <div key={`userRow-${index}`} className='row grid-row pt-3 pb-3 border-bottom'>
              <div className='col-12 col-md-3 pr-0'>
                <Link className='font-weight-bold' to={{pathname: `/admin/users/${user.Login}`}}>{user.Login}</Link>
              </div>
              <div className='col-12 col-md-3 pr-0 text-truncate'>
                <div className='d-inline-block'>
                  <span className='font-weight-bold d-xl-none'>Email:&nbsp;</span>{user.Email}</div>
              </div>
              <div className='col-12 col-md-3 pr-0 text-truncate'>
                <span className='font-weight-bold d-xl-none'>Роли:&nbsp;</span>
                {user.Roles.map((role, index) => (
                  <div className='d-inline-block mr-1' key={`roleelem-${index}`}>
                    <span className="badge badge-primary">{role.ShortId}</span>
                  </div>))}
              </div>
              <div className='col-12 col-md-3 pr-0 text-truncate'>
                <div className='d-inline-block'>
                  <span className='font-weight-bold d-xl-none'>Последняя активность:&nbsp;</span>2019-11-01 12:14</div>
              </div>
            </div>))}
        </div>
      </div>
    </div>
  )
}

export default class AdminUsersPage extends Component {
  constructor(props) {
    super(props)
    const queryParams = this.props.location.search ? queryString.parse(this.props.location.search) : null
    const cookies = new Cookies()
    const allCookies = cookies.getAll()
    const auth = {username: allCookies.AuthToken, password: allCookies.RefreshToken}
    this.state = {
      sessionIsAlive: (auth.username || auth.password) ? true : false,
      users: {
        list: [],
        totalPages: 1,
        currentPage: 1
      },
      needReload: false,
      loading: {
        searchUsers: false,
        getMyProfile: false
      },
      error: {errorCode: null, errorText: null},
      success: null,
      modals: {},
      searchForm: {
        login: queryParams && queryParams.login ? queryParams.login : '',
        email: queryParams && queryParams.email ? queryParams.email : '',
      }
    }
  }
  componentDidMount = () => {this.setState({...this.state, needReload: true})}
  componentDidUpdate = () => {
    const {state} = this
    const {loading} = state
    const cookies = new Cookies()
    const allCookies = cookies.getAll()
    const auth = {username: allCookies.AuthToken, password: allCookies.RefreshToken}
    if (this.state.needReload && !loading.searchUsers) searchUsers(state.searchForm, this, auth)
  }
  handleSearchFormChange = (event) => {
    const {searchForm} = this.state
    switch (event.currentTarget.id) {
    case 'login':
      this.setState({...this.state,
        searchForm: {...searchForm, login: event.currentTarget.value}})
      break
    case 'email':
      this.setState({...this.state,
        searchForm: {...searchForm, email: event.currentTarget.value}})
      break
    }
  }
  clearSearchForm = () => {this.setState({...this.state, searchForm: {login: '', perPage: '10', page: '1', email: ''}})}
  render() {
    const {props, state, handleSearchFormChange, clearSearchForm} = this
    const {searchForm, error, users, success, loading, sessionIsAlive} = state
    const {location, user} = props
    const {totalPages, currentPage} = users
    const cookies = new Cookies()
    const allCookies = cookies.getAll()
    if (!allCookies.AuthToken && !allCookies.RefreshToken) {
      return <Redirect to={{pathname: "/login"}}/>
    } else {
    return (
      <Page>
        <div className='row' style={{minHeight: 'calc(100vh - 112px)'}}>
          <div className='col-12'>
            {success ? <SuccessMessage closeAction={()=>{this.setState({...state, success: null})}}>{success}</SuccessMessage> : null}
            <Form>
              <TextFieldInput id='login' header='Логин' value={searchForm.login} isValid disabled={loading.searchUsers}
                adaptiveClasses='col-12 col-sm-4 col-md-3' action={() => {window.location.href = `/admin/users${getSearchUrlFromObject('1', searchForm)}`}}
                changeValue={handleSearchFormChange} clearValue={()=>{this.setState({...this.state, searchForm: {...searchForm, login: ''}})}}/>
              <TextFieldInput id='email' header='Email' value={searchForm.email} isValid disabled={loading.searchUsers}
                adaptiveClasses='col-12 col-sm-4 col-md-3' action={() => {window.location.href = `/admin/users${getSearchUrlFromObject('1', searchForm)}`}}
                changeValue={handleSearchFormChange} clearValue={()=>{this.setState({...this.state, searchForm: {...searchForm, email: ''}})}}/>
              <ListField isValid changeValue={handleSearchFormChange} disabled={loading.searchSms} adaptiveClasses='col-12 col-sm-4 col-md-3'
                valuesList={[{value: 5, verboseValue: 5}, {value: 10, verboseValue: 10}, {value: 20, verboseValue: 20}, {value: 50, verboseValue: 50}]}
                header='Показать' id='perPage' value={searchForm.perPage}/>
              <div className='btn-group btn-block col-12 col-md-2 align-self-end mt-0' role='group'
                data-toggle='tooltip' data-placement='top' title='Искать / Очистить форму' style={{marginBottom: '1.5rem'}}>
                <LinkButton loading={loading.searchTemplates} link={`/admin/users${getSearchUrlFromObject(1, searchForm)}`} onClick={() => {this.setState({...state, needReload: true})}}><i className='fas fa-search' /></LinkButton>
                <Button color='secondary' loading={loading.getTemplate} action={clearSearchForm}><i className='fas fa-times' /></Button>
              </div>
            </Form>
            {error.errorText ? <ErrorMessage>{error.errorText}</ErrorMessage> : null}
            {!sessionIsAlive ? <ErrorMessage>Пользователь не авторизован!</ErrorMessage> : null}
            {!loading.searchUsers && !error.errorText && users.list.length == 0 ? <WarningMessage>По запросу пользователей не найдено!</WarningMessage> : null}
            {!error.errorCode && users.list.length != 0 ? <UsersSearchResultBlock usersList={users.list} loading={loading.searchUsers}/> : null}
            {loading.searchUsers && users.list.length == 0 ? <SearchPreloader /> : null}
          </div>
          <div className='col-12 align-self-end'>
            {(totalPages && totalPages > 1) ? <div className='row'><div className='col-12 mt-3'><Pagination totalPages={totalPages} currentPage={currentPage} location={location} /></div></div> : null}
          </div>
        </div>
      </Page>)
    }
  }
}