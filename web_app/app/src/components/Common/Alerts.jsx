import React, {Component} from 'react'
import {Fade} from 'react-reveal'

export class Alert extends Component {
  constructor(props) {super(props)}
  componentDidMount = () => {if (this.props.timeOut) {setTimeout(this.props.closeAction, 5000)}}
  render() {
    const {props} = this
    const {alertType, children, closeAction} = props
    return (
      <Fade>
        <div className={`row alert alert-${alertType} ml-1 mr-1 mr-md-0 ml-md-0`} role='alert'>
          <div className={closeAction ? 'col-10 col-sm-11' : 'col-12'}>{children}</div>
          {closeAction ?
            <div className='col-2 col-sm-1 text-right'><i className='fas fa-times p-1' style={{cursor: 'pointer'}} onClick={props.closeAction}></i></div> : null}
        </div>
      </Fade>
    )
  }
}

export const ErrorMessage = props =>
  <Alert alertType='danger' closeAction={props.closeAction}>
    <div className='row'>
      <div className='col-2 col-md-1 text-danger text-center d-flex' style={{alignItems: 'center', justifyContent: 'center'}}>
        <i className='fas fa-exclamation-circle' style={{fontSize: '1.5rem'}}/>
      </div>
      <div className='col-10 col-md-11'>{props.children}</div>
    </div>
  </Alert>

export const WarningMessage = props =>
  <Alert alertType='warning' closeAction={props.closeAction}>
    <div className='row'>
      <div className='col-2 col-md-1 text-warning text-center d-flex' style={{alignItems: 'center', justifyContent: 'center'}}>
        <i className='fas fa-exclamation-triangle' style={{fontSize: '1.5rem'}}/>
      </div>
      <div className='col-10 col-md-11'>{props.children}</div>
    </div>
  </Alert>

export const InfoMessage = props =>
  <Alert alertType='info' closeAction={props.closeAction}>
    <div className='row'>
      <div className='col-2 col-md-1 text-info text-center d-flex' style={{alignItems: 'center', justifyContent: 'center'}}>
        <i className='fas fa-info-circle' style={{fontSize: '1.5rem'}}/>
      </div>
      <div className='col-10 col-md-11'>{props.children}</div>
    </div>
  </Alert>

export const SuccessMessage = props =>
  <Alert alertType='success' closeAction={props.closeAction}>
    <div className='row'>
      <div className='col-2 col-md-1 text-success text-center d-flex' style={{alignItems: 'center', justifyContent: 'center'}}>
        <i className='fas fa-check-circle' style={{fontSize: '1.5rem'}}/>
      </div>
      <div className='col-10 col-md-11'>{props.children}</div>
    </div>
  </Alert>

export default Alert