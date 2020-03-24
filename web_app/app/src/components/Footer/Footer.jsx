import React, { Component } from 'react'

class Footer extends Component {
  render() {
    const today = new Date()
    return (
      <footer>
        <nav className='navbar navbar-expand-lg navbar-dark bg-primary'>
          <span className='text-light'>&#169; Кружечкин Дмитрий {today.getFullYear()}</span>
        </nav>
      </footer>
    );
  }
}

export default Footer