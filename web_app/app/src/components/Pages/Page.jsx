import React from 'react'

export const Page = (props) =>
  <main style={{minHeight: 'calc(100vh - 96px)'}}>
    <div className='container pt-3'>{props.children}</div>
  </main>

export default Page