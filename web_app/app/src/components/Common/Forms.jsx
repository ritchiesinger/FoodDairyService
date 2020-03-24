import React from 'react'
import {Link} from 'react-router-dom'
import {Zoom} from 'react-reveal'
require('moment/locale/ru')
import Datetime from 'react-datetime'
import './Forms.css'


export const Form = (props) => <div className='row'>{props.children}</div>

export const TextAreaInput = (props) => {
  const {id, header, rows, adaptiveClasses, value, changeValue, monospaceFont, readOnly, isEdited, isValid, validationText, max} = props
  let style={outline: 'none', boxShadow: 'none'}
  if (monospaceFont) style['fontFamily'] = 'monospace'
  return (
    <div className={`form-group${adaptiveClasses ? ' ' + adaptiveClasses : ''}`} >
      <label htmlFor={id}>{header}</label>
      <textarea className='form-control' id={id} rows={rows} value={value} onChange={changeValue} style={style} maxLength={max ? max : ''}
        readOnly={readOnly} style={{backgroundColor: isEdited ? '#fff3cd' : '#fff', borderColor: !isValid ? '#dc3545' : '#ced4da'}}/>
      <Zoom><small className='form-text text-danger'>{validationText && !isValid ? validationText : <span>&nbsp;</span>}</small></Zoom>
    </div>
  )
}

export const TextFieldInput = (props) => {
  const {
    required,
    helpText, // Текст-подсказка. Если передан, то в заголовке поля будет значок с тултипом, при наведении отображающим этот текст
    lockText, // Текст-причина блокировки поля (будет отображаться значок с тултипом в заголовке поля)
    type, // Тип текстового поля (text/number/email и т.д)
    validationText, // Текст, отображаемый красным цветом под полем в случае если isValid = false
    isValid, // Признак валидности введённого значения
    isEdited, // Признак того, что значение в поле было изменено (поле подкрасится)
    header, // заголовок поля
    placeholder, // плейсхолдер
    id, // Идентификатор поля
    value, // Значение поля
    disabled, // Признак блокировки поля
    readOnly, // Признак только на чтение
    adaptiveClasses, // Строка из любых классов, которые добавятся к уже существующим у компонента
    action, // Функция, которая будет выполнена при нажатии на Enter когда фокус на компоненте
    changeValue, // Функция, которая будет выполнена когда компонент изменит значение
    clearValue, // Функция, которая будет выполнена при нажатии на крест
    maxLength
  } = props
  return (
    <div className={`form-group mb-0${adaptiveClasses ? ' ' + adaptiveClasses : ''}`}>
      <label htmlFor={id}>{header}{required ? <span className='text-danger ml-2'>*</span> : null}
        {lockText ? <Zoom><i className='fas fa-exclamation-triangle text-warning ml-2' data-toggle='tooltip' data-placement='top' title={lockText} style={{cursor: 'help'}}/></Zoom> : null}
        {helpText ? <i className='far fa-question-circle text-primary ml-1' style={{cursor: 'help'}} data-toggle='tooltip' title={helpText}/> : null}
      </label>
      <div className='input-group'>
        <input id={id} placeholder={placeholder} type={type ? type : 'text'} className='form-control' readOnly={readOnly} maxLength={maxLength ? maxLength : ''}
          onKeyDown={(event) => {if (event.key == 'Escape') {clearValue()} else if (event.key == 'Enter') {action ? action() : () => {} }}}
          value={value} onChange={changeValue} disabled={disabled || lockText} tabIndex='1'
          style={{borderColor: !isValid ? '#dc3545' : '#ced4da', borderRight: value && !disabled && !readOnly && clearValue ? '1px solid #fff' : !isValid ? '1px solid #dc3545' : '1px solid #ced4da',
            backgroundColor: !disabled ? isEdited ? '#fff3cd' : '#fff' : '#e9ecef', outline: 'none', boxShadow: 'none'}}/>
        <div className={`input-group-append${!value || disabled || readOnly || !clearValue ? ' d-none' : ''}`} data-toggle='tooltip' data-placement='top' title='Очистить поле'>
          <div className='input-group-text' data-for={id} onClick={clearValue}
            style={{cursor: 'pointer', borderLeft: '1px solid #fff', backgroundColor: isEdited ? '#fff3cd' : '#fff'}}>
            <i className='fas fa-times'/>
          </div>
        </div>
      </div>
      <Zoom><small className='form-text text-danger'>{validationText && !isValid ? validationText : <span>&nbsp;</span>}</small></Zoom>
    </div>
  )
}

export const DateTimeInput = props => {
  // Компонент основан на стороннем DateTimePicker - https://github.com/YouCanBookMe/react-datetime
  const {
    required,
    helpText, // Текст-подсказка. Если передан, то в заголовке поля будет значок с тултипом, при наведении отображающим этот текст
    lockText, // Текст-причина блокировки поля (будет отображаться значок с тултипом в заголовке поля)
    validationText, // Текст, отображаемый красным цветом под полем в случае если isValid = false
    isValid, // Признак валидности введённого значения
    isEdited, // Признак того, что значение в поле было изменено (поле подкрасится)
    header, // заголовок поля
    id, // Идентификатор поля
    value, // Значение поля
    disabled, // Признак блокировки поля
    adaptiveClasses, // Строка из любых классов, которые добавятся к уже существующим у компонента
    action, // Функция, которая будет выполнена при нажатии на Enter когда фокус на компоненте
    changeValue, // Функция, которая будет выполнена когда компонент изменит значение
    readOnly,
    clearValue
  } = props
  return (
    <div className={`form-group mb-0${adaptiveClasses ? ' ' + adaptiveClasses : ''}`}>
      <label htmlFor={id}>{header}{required ? <span className='text-danger ml-2'>*</span> : null}
        {lockText ? <Zoom><i className='fas fa-exclamation-triangle text-warning ml-2' data-toggle='tooltip' data-placement='top' title={lockText} style={{cursor: 'help'}}/></Zoom> : null}
        {helpText ? <i className='far fa-question-circle text-primary ml-1' style={{cursor: 'help'}} data-toggle='tooltip' title={helpText}/> : null}
      </label>
      <div className='input-group'>
        <Datetime value={value} onChange={changeValue} closeOnSelect={true} closeOnTab={true} className={`form-control`}
          inputProps={{
            id: id, onKeyDown: (event) => {if (event.key == 'Enter') {action ? action() : () => {}}},
            disabled: disabled || lockText,
            readOnly: true,
            style: {
              border: 0,
              borderColor: !isValid ? '#dc3545' : '#ced4da',
              backgroundColor: !disabled ? isEdited ? '#fff3cd' : 'transparent' : '#e9ecef',
              outline: 'none',
              boxShadow: 'none'
            }
          }}/>
        <div className={`input-group-append${!value || disabled || readOnly || !clearValue ? ' d-none' : ''}`} data-toggle='tooltip' data-placement='top' title='Очистить поле'>
          <div className='input-group-text' data-for={id} onClick={clearValue}
            style={{cursor: 'pointer', borderLeft: '1px solid #fff', backgroundColor: isEdited ? '#fff3cd' : '#fff'}}>
            <i className='fas fa-times'/>
          </div>
        </div>
      </div>
      <Zoom><small className='form-text text-danger'>{validationText && !isValid ? validationText : <span>&nbsp;</span>}</small></Zoom>
    </div>
  )
}

export const ListField = (props) => {
  const {
    required,
    header, // Заголовок поля
    id, // Идентификатор поля
    value, // Значение поля
    allValues, // В списке будет присутствовать пункт "Все" который будет передавать пустое значение параметра
    helpText, // Текст с подсказкой. Если передан в заголовке будет значок с тултипом соответственно с этим текстом
    validationText, // При isValid = false этот текст будет отображаться под полем красным цветом
    isValid, // Признак валидности значения введённого в поле
    noSelect, // В списке будет присутствовать пункт "Не выбрано" который будет передавать пустое значение параметра
    isEdited, // Признак было ли значение отредактировано (поле будет подкрашено)
    loading, // В заголовке будет отображаеться спинер, когда передан этот признак
    adaptiveClasses, // любая строка с классами которая будет добавлена к значению class элемента
    disabled, // Признак заблокированности эелемента
    changeValue // Функция callback вызываемая при изменении значения value элемента
  } = props
  const locker = props.locker ? props.locker : {} // Чтобы было дефолтное значение
  const {isLocked, lockWarning} = locker
  const valuesList = props.valuesList ? props.valuesList : []
  return (
    <div className={`form-group mb-0${adaptiveClasses ? ` ${adaptiveClasses}` : ''}`}>
      <label htmlFor={id}>{header}{required ? <span className='text-danger ml-2'>*</span> : null}
        {isLocked ?
          <i className='fas fa-exclamation-triangle text-warning ml-2' style={{cursor: 'help'}}
            data-toggle='tooltip' data-placement='top' title={lockWarning}/> : null}
        {helpText ?
          <i className='far fa-question-circle text-primary ml-2' style={{cursor: 'help'}}
            data-toggle='tooltip' title={helpText}/> : null}
        {loading ? <span className='spinner-border spinner-border-sm text-primary ml-2' role='status' aria-hidden='true'/> : null}
      </label>
      <select id={id} className='form-control' onChange={changeValue} value={value} disabled={disabled || isLocked}
        style={{outline: 'none', boxShadow: 'none',
          borderColor: !isValid ? '#dc3545' : '#ced4da',
          backgroundColor: !disabled ? isEdited ? '#fff3cd' : '#fff' : "#e9ecef"}}>
        {noSelect ? <option value=''>Не выбрано</option> : null}
        {allValues ? <option value=''>Все</option> : null}
        {valuesList.map((valueItem, valueIndex) => (
          <option key={`${id}-${valueIndex}`} value={valueItem.value}>{valueItem.verboseValue}</option>))}
      </select>
      <small className='form-text text-danger'>{validationText && !isValid ? validationText : <span>&nbsp;</span>}</small>
    </div>
  )
}

export const CheckBox = (props) => {
  const {header, checked, id, adaptiveClasses, changeCallback, disabled} = props
  return (
    <div className={adaptiveClasses}>
      <div className='form-check'>
        <input id={id} type='checkbox' className='form-check-input' onChange={changeCallback} checked={checked} disabled={disabled} />
        <label className='form-check-label' htmlFor={id}>{header}</label>
      </div>
    </div>
  )
}

export const LinkButton = (props) => {
  const {children, loading, link, disabled, color, btnBlock, loadingText, tooltip, small, adaptiveClasses, onClick} = props
  return (
    <Link className={`btn btn-${color ? color : 'primary'}${adaptiveClasses ? ' ' + adaptiveClasses : ''}${small ? ' btn-sm' : ''}${btnBlock ? ' btn-block' : ''}${loading || disabled ? ' disabled' : ''}`}
      to={link} style={{outline: 'none', boxShadow: 'none'}} data-toggle='tooltip' data-placement='top' title={tooltip ? tooltip : null} onClick={onClick}>
      {loadingText && loading ?
        <span><span className='spinner-border spinner-border-sm mr-2' role='status' aria-hidden='true'></span>{loadingText}</span> : children}
    </Link>
  )
}

export const Button = (props) => {
  const {
    children, 
    loading, 
    action, 
    disabled, 
    color, 
    btnBlock, 
    loadingText, 
    fixedWidth, 
    role, 
    adaptiveClasses, 
    tooltip
  } = props
  const buttonStyle = {
    outline: 'none',
    boxShadow: 'none',
    cursor: disabled || loading ? 'default' : 'pointer',
  }
  if (fixedWidth) buttonStyle['width'] = fixedWidth
  return (
    <button className={`btn btn-${color ? color : 'primary'}${adaptiveClasses ? ' ' + adaptiveClasses : ''}${btnBlock ? ' btn-block' : ''}${loading || disabled ? ' disabled' : ''}`}
      onClick={disabled || loading ? null : action} data-role={role} style={buttonStyle}  data-toggle='tooltip' data-placement='top' title={tooltip ? tooltip : null}>
      {loadingText && loading ?
        <span><span className='spinner-border spinner-border-sm mr-2' role='status' aria-hidden='true'></span>{loadingText}</span> : children}
    </button>
  )
}

export const DatePicker = (props) => {
  const {header, value, required, id, adaptiveClasses, changeCallback, disabled, validationText, isValid} = props
  return (
    <div className={'form-group' + adaptiveClasses ? ` ${adaptiveClasses}` : ''}>
      <label htmlFor={id}>{header}{required ? <span className='text-danger'>&nbsp;*</span> : null}</label>
      <input id={id} type='date' className={!isValid ? 'form-control border border-danger' : 'form-control'}
        onChange={changeCallback} value={value}
        disabled={disabled} />
      {!isValid ? <h6 className='text-danger mt-1' style={{fontSize: '80%'}}>{validationText}</h6> :
        <h6 className='mt-1' style={{fontSize: '80%'}}>&nbsp;</h6>}
    </div>
  )
}

export default TextFieldInput