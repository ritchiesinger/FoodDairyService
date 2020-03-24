import React, {Component} from 'react'
import { Link, NavLink } from 'react-router-dom'
import Logo from 'assets/logo.png'
import Cookies from 'universal-cookie'
const logoStyle = {
  width: '30px',
  height: '30px',
  backgroundImage: `url(static/${Logo})`,
  backgroundColor: 'transparent',
  backgroundSize: 'contain',
  backgroundPosition: 'center',
  backgroundRepeat: 'no-repeat'
}

export const LeftMenu = props => <div className='collapse navbar-collapse' id='navBarMenu'><div className='navbar-nav'>{props.children}</div></div>

export const RightMenu = props => <div className='collapse navbar-collapse flex-row-reverse' id='navBarMenu'><div className='navbar-nav'>{props.children}</div></div>

export const Header = props => {
  const {user, logout} = props
  return (
    <header>
      <nav className='navbar navbar-expand-lg navbar-dark bg-primary'>
        <Link to={'/'} className='navbar-brand'><div className='brand-logo' style={logoStyle} /></Link>
        <button className='navbar-toggler' type='button' data-toggle='collapse' data-target='#navBarMenu'
          aria-controls='navBarMenu' aria-expanded='false' aria-label='Toggle navigation'>
          <span className='navbar-toggler-icon'></span>
        </button>
        {user.login ?
          <LeftMenu>
            <NavLink to='/measures' className='nav-item nav-link' activeClassName='nav-item nav-link active' isActive={(match, location) => ['/measures'].includes(location.pathname)}>Метрики</NavLink>
            <NavLink to='/fooddairy' className='nav-item nav-link' activeClassName='nav-item nav-link active' isActive={(match, location) => ['/fooddairy'].includes(location.pathname)}>Дневник</NavLink>
            <div className="nav-item dropdown">
              <a className="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                Администрирование
              </a>
              <div className="dropdown-menu" aria-labelledby="navbarDropdown">
                <NavLink to='/admin/users' className='dropdown-item' activeClassName='dropdown-item active' isActive={(match, location) => ['/admin/users'].includes(location.pathname)}>Пользователи</NavLink>
                <NavLink to='/admin/roles' className='dropdown-item' activeClassName='dropdown-item active' isActive={(match, location) => ['/admin/roles'].includes(location.pathname)}>Роли</NavLink>
                <NavLink to='/admin/functions' className='dropdown-item' activeClassName='dropdown-item active' isActive={(match, location) => ['/admin/functions'].includes(location.pathname)}>Функции</NavLink>
              </div>
            </div>
          </LeftMenu> : null}
        <RightMenu>
          {user.login ? 
            <span className='nav-item nav-link disabled' style={{color: 'rgba(255,255,255,.5)'}}>{user.login}</span> :
            <NavLink to='/registration' className='nav-item nav-link' activeClassName='nav-item nav-link active' isActive={(match, location) => ['/registration'].includes(location.pathname)}>Регистрация</NavLink>}
          {user.login ? 
            <a className='nav-item nav-link' onClick={logout} style={{cursor: 'pointer'}}>Выйти</a> :
            <NavLink to='/login' className='nav-item nav-link' activeClassName='nav-item nav-link active' isActive={(match, location) => ['/login'].includes(location.pathname)}>Войти</NavLink>}
        </RightMenu>
      </nav>
    </header>
  )
}

export default Header