import React from 'react'
import { Link } from 'react-router-dom'
import queryString from 'query-string'

function range(start, edge, step) {
  // If only 1 number passed make it the edge and 0 the start
  if (arguments.length === 1) {
    edge = start
    start = 0
  }
  // Validate edge/start
  edge = edge || 0
  step = step || 1
  // Create array of numbers, stopping before the edge
  let arr = []
  for (arr; (edge - start) * step > 0; start += step) {
    arr.push(start)
  }
  return arr
}

const generateLink = (newPage, location) => {
  const {search, pathname} = location
  let paramsObj = queryString.parse(search)
  if (!paramsObj.page) paramsObj.page = 1
  if (!paramsObj.perPage) paramsObj.perPage = 10
  let paramsString = `${pathname}?`
  for (let formField in paramsObj) {
    if (paramsObj[formField]) paramsString += (formField == 'page' ? `page=${newPage}&` : `${formField}=${paramsObj[formField]}&`)
  }
  return paramsString.slice(0, -1)
}

const PaginationBlock = (props) =>
  <nav>
    <ul className='d-block d-sm-flex pagination noselect pagination-block text-center'>
      <PaginationItem disabled={props.currentPage == 1} pageNumber={props.currentPage - 1} location={props.location} char={<i className='fas fa-angle-left' />}/>
      {props.children}
      <PaginationItem disabled={props.totalPages == props.currentPage} pageNumber={props.currentPage + 1} location={props.location} char={<i className='fas fa-angle-right' />}/>
    </ul>
  </nav>

const PaginationItem = (props) => {
  const {disabled, active, pageNumber, location, char, mobileHide} = props
  return (
    <li style={{cursor: active ? 'default' : 'pointer', width: '60px'}}
      className={`${mobileHide ? 'd-none d-sm-inline-block' : 'd-inline-block'} page-item${disabled ? ' disabled' : ''}${active ? ' active' : ''}`}>
      <Link className='page-link' to={generateLink(pageNumber, location)} style={{outline: 'none', boxShadow: 'none'}}>{char}</Link>
    </li>
  )
}

export const Pagination = (props) => {
  const {currentPage, totalPages, location} = props
  return (
    <PaginationBlock currentPage={currentPage} totalPages={totalPages} location={location}>
      {/* Когда всего страниц меньше или равно 9 */}
      {totalPages <= 9 ? range(1, totalPages + 1).map((pageNumber) => (
        <PaginationItem mobileHide key={`pagination-link-${pageNumber}`} active={currentPage == pageNumber} pageNumber={pageNumber} location={location} char={pageNumber}/>)) : null}
      {/* Когда страниц больше 9 и номер текущей страницы больше 4 и меньше на 4 чем кол-во страниц всего */}
      {totalPages > 9 && currentPage > 4 && currentPage <= totalPages - 5 ? <PaginationItem mobileHide key={`pagination-link-1`} pageNumber='1' location={location} char='1'/> : null}
      {totalPages > 9 && currentPage > 4 && currentPage <= totalPages - 5 ? <PaginationItem mobileHide key={`pagination-link-${currentPage - 2}`} pageNumber={currentPage - 2} location={location} char='...'/> : null}
      {totalPages > 9 && currentPage > 4 && currentPage <= totalPages - 5 ? range(currentPage - 1, currentPage + 2).map((pageNumber) => (
        <PaginationItem mobileHide key={`pagination-link-${pageNumber}`} active={currentPage == pageNumber} pageNumber={pageNumber} location={location} char={pageNumber}/>)) : null}
      {totalPages > 9 && currentPage > 4 && currentPage <= totalPages - 5 ? <PaginationItem mobileHide key={`pagination-link-${currentPage + 2}`} pageNumber={currentPage + 2} location={location} char='...'/> : null}
      {totalPages > 9 && currentPage > 4 && currentPage <= totalPages - 5 ? <PaginationItem mobileHide key={`pagination-link-${totalPages}`} pageNumber={totalPages} location={location} char={totalPages}/> : null}
      {/* Когда всего больше 9, а текущая страница до 4й включительно */}
      {totalPages > 9 && currentPage <= 4 ? range(1, 6).map((pageNumber) => (
        <PaginationItem mobileHide key={`pagination-link-${pageNumber}`} active={currentPage == pageNumber} pageNumber={pageNumber} location={location} char={pageNumber}/>)) : null}
      {totalPages > 9 && currentPage <= 4 ? <PaginationItem mobileHide key={`pagination-link-6`} pageNumber='6' location={location} char='...'/> : null}
      {totalPages > 9 && currentPage <= 4 ? <PaginationItem mobileHide key={`pagination-link-${totalPages}`} pageNumber={totalPages} location={location} char={totalPages}/> : null}
      {/* Когда всего больше 9, а текущая страница от 4й с конца и до последней */}
      {totalPages > 9 && totalPages - currentPage <= 4 ? <PaginationItem mobileHide key={`pagination-link-1`} pageNumber='1' location={location} char='1'/> : null}
      {totalPages > 9 && totalPages - currentPage <= 4 ? <PaginationItem mobileHide key={`pagination-link-${totalPages - 5}`} pageNumber={totalPages - 5} location={location} char='...'/> : null}
      {totalPages > 9 && totalPages - currentPage <= 4 ? range(totalPages - 4, totalPages + 1).map((pageNumber) => (
        <PaginationItem mobileHide key={`pagination-link-${pageNumber}`} active={currentPage == pageNumber} pageNumber={pageNumber} location={location} char={pageNumber}/>)) : null}
    </PaginationBlock>
  )
}

export default Pagination