import axios from 'axios'
import Cookies from 'universal-cookie'

const registrationRequest = contract => {
  const requestURL = '/api/SignUp/'
  console.log(`Запрос на регистрацию нового пользователя: ${requestURL}. Тело запроса:`, contract)
  return axios.post(requestURL, contract)
}

const getTokensRequest = auth => {
  const requestURL = '/api/GetToken/'
  console.log(`Запрос на получение токенов (авторизация): ${requestURL}`)
  return axios.get(requestURL, {auth: auth})
}

const getMyProfileRequest = auth => {
  const requestURL = '/api/GetMyProfile/'
  console.log(`Запрос на получение информации об авторизованном пользователе: ${requestURL}`)
  return axios.get(requestURL, {auth: auth})
}

const searchUsersRequest = (filter, auth) => {
  const requestParams = {
    login: filter.login,
    email: filter.email
  }
  let paramsString = '?'
  for (let formField in requestParams) {
    paramsString = requestParams[formField] && requestParams[formField] != '' ? paramsString + `${formField}=${requestParams[formField]}&` : paramsString
  }
  const requestURL = `/api/Users/${paramsString ? `${paramsString.slice(0, -1)}` : ''}`
  console.log(`Запрос на поиск пользователей: ${requestURL}`, '. Авторизация:', auth)
  return axios.get(requestURL, {auth: auth})
}

const checkNewTokens = (NewTokens) => {
  const cookies = new Cookies()
  if (NewTokens && (NewTokens.AuthToken || NewTokens.RefreshToken)) {
    if (NewTokens.AuthToken) cookies.set('AuthToken', NewTokens.AuthToken, {maxAge: 30})
    if (NewTokens.RefreshToken) cookies.set('RefreshToken', NewTokens.RefreshToken, {maxAge: 90})
    console.log('Устанавливаем в cookie новые токены:', NewTokens)
  }
}

// Обёртки запросов для использования в компонентах React

export const registration = (contract, component) => {
  component.setState({...component.state,
    loading: {...component.state.loading, registration: true},
    error: {errorCode: null, errorText: null}
  })
  registrationRequest(contract).then(
    response => {
      const {data} = response
      const {Data} = data
      const {User, AuthToken, RefreshToken} = Data
      console.log(`Результат запроса регистрации:`, data)
      component.setState({...component.state,
        loading: {...component.state.loading, registration: false},
        error: {errorCode: null, errorText: null},
        registrationSuccess: true
      })
    }
  )
  .catch(
    error => {
      console.log(error)
      const {status, statusText} = error.response
      let errorText
      if (status == 403) {
        errorText = `Неверный логин или пароль!`
        console.error(errorText)
      } else {
        errorText = `Ошибка при запросе к серверу: ${status} (${statusText})`
        console.error(errorText)
      }
      component.setState({...component.state,
        loading: {...component.state.loading, registration: false},
        error: {errorCode: status, errorText: errorText},
        registrationSuccess: false
      })
    }
  )
}

export const getTokens = (auth, component) => {
  component.setState({...component.state,
    loading: {...component.state.loading, login: true},
    error: {errorCode: null, errorText: null}
  })
  getTokensRequest(auth).then(
    response => {
      const {data} = response
      const {Data} = data
      const {User, AuthToken, RefreshToken} = Data
      console.log(`Результат запроса токенов:`, data)
      const cookies = new Cookies()
      cookies.set('AuthToken', AuthToken, {maxAge: 30})
      cookies.set('RefreshToken', RefreshToken, {maxAge: 90})
      console.log('Установлены cookies: ', cookies.getAll())
      component.setState({...component.state,
        user: {login: User.Login, email: User.Email, roles: []},
        loading: {...component.state.loading, login: false},
        error: {errorCode: null, errorText: null}
      })
    }
  )
  .catch(
    error => {
      const {status, statusText} = error.response
      let errorText
      if (status == 403) {
        errorText = `Неверный логин или пароль!`
        console.error(errorText)
      } else {
        errorText = `Ошибка при запросе к серверу: ${status} (${statusText})`
        console.error(errorText)
      }
      component.setState({...component.state,
        loading: {...component.state.loading, login: false},
        error: {errorCode: status, errorText: errorText}
      })
    }
  )
}

export const getMyProfile = (auth, component) => {
  component.setState({
    ...component.state,
    loading: {...component.state.loading, getMyProfile: true},
    error: {errorCode: null, errorText: null}
  })
  getMyProfileRequest(auth).then(
    response => {
      const {data} = response
      console.log(`Результат запроса профиля:`, data)
      const {Data} = data
      const {NewTokens} = Data
      checkNewTokens(NewTokens) // Проверка получения свежих токенов и их установка
      component.setState({...component.state,
        user: {login: Data.Login, email: Data.Email, roles: []},
        loading: {...component.state.loading, getMyProfile: false},
        error: {errorCode: null, errorText: null}
      })
    }
  )
  .catch(
    error => {
      console.log('catch')
      if (error.response) {
        const {status, statusText} = error.response
        let errorText
        if (status == 403) {
          errorText = `Неверный логин или пароль!`
          console.error(errorText)
        } else {
          errorText = `Ошибка при запросе к серверу: ${status} (${statusText})`
          console.error(errorText)
        }
        component.setState({...component.state,
          loading: {...component.state.loading, getMyProfile: false},
          error: {errorCode: status, errorText: errorText}
        })
      } else {
        console.log(error)
      }
    }
  )
}

export const searchUsers = (filter, component, auth) => {
  component.setState({
    ...component.state,
    loading: {...component.state.loading, searchUsers: true},
    error: {errorCode: null, errorText: null}
  })
  searchUsersRequest(filter, auth).then(
    response => {
      const {data, status} = response
      const {ErrorCode, ErrorText, Data} = data
      const {NewTokens} = Data
      checkNewTokens(NewTokens) // Проверка получения свежих токенов и их установка
      console.log(`Результат поиска пользователей:`, data)
      if (status == 200 && ErrorCode == 0) {      
        component.setState({...component.state,
          needReload: false,
          loading: {...component.state.loading, searchUsers: false},
          error: {errorCode: null, errorText: null},
          users: {
            list: data.Data.UsersList,
            totalPages: Data.totalPages,
            currentPage: Data.currentPage
          }
        })
      } else {
        component.setState({...component.state,
          loading: {...component.state.loading, searchUsers: false},
          error: {errorCode: ErrorCode, errorText: ErrorText}
        })
      }
    }
  )
  .catch(
    error => {
      const {status, statusText} = error.response
      console.log(status)
      let errorText
      if (status == 403) {
        errorText = 'Время сессии истекло! Авторизуйтесь повторно для продолжения работы!'
      } else {
        errorText = `Ошибка при запросе к серверу: ${status} (${statusText})`
      }
      console.error(errorText)
      component.setState({...component.state,
        loading: {...component.state.loading, searchUsers: false},
        error: {errorCode: status, errorText: errorText}
      })
    }
  )
}