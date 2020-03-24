import React from 'react'
import {Link} from 'react-router-dom'
import moment from 'moment'

export const logout = (component) => {
  const cookies = new Cookies()
  cookies.remove("AuthToken")
  cookies.remove('RefreshToken')
  console.log('Установлены cookies: ', cookies.getAll())
  component.setState({...component.state,
    sessionIsAlive: false,
    needReload: true
  })
}

export const decodeHtml = (html) => {
  var txt = document.createElement("textarea");
  txt.innerHTML = html;
  return txt.value;
}

export const BreadCrumbs = (props) => {
  const {curentLocationName, prevUrl, prevLocationName} = props
  return (
    <div className='row'>
      <div className='col mt-3'>
        <nav aria-label='breadcrumb' className='w-100'>
          <ol className='breadcrumb'>
            <li className='breadcrumb-item'><Link to={prevUrl}>{prevLocationName}</Link></li>
            <li className='breadcrumb-item active' aria-current='page'>{curentLocationName}</li>
          </ol>
        </nav>
      </div>
    </div>
  )
}

export const SearchPreloader = () =>
  <div className='row'>
    <div className='col-12 text-center mt-3'>
      <span className='spinner-grow text-primary' role='status' aria-hidden='true'/>
      <span className='spinner-grow text-primary' role='status' aria-hidden='true'/>
      <span className='spinner-grow text-primary' role='status' aria-hidden='true'/>
    </div>
  </div>
export default SearchPreloader

export const getSearchUrlFromObject = (page, object) => {
  const searchForm = object
  let paramsString = '?'
  for (let formField in searchForm) {
    if (formField == 'page') {
      paramsString += `page=${page}&`
    } else if (['dateCreateFrom', 'dateCreateTo', 'dateFinishedFrom', 'dateFinishedTo'].includes(formField)) {
      paramsString = searchForm[formField] ? paramsString + `${formField}=${moment(searchForm[formField]).format("YYYY-MM-DDTHH:mm:ss")}&` : paramsString
    } else {
      paramsString = searchForm[formField] ? paramsString + `${formField}=${searchForm[formField]}&` : paramsString
    }
  }
  return paramsString.slice(0, -1)
}