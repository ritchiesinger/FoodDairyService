import React, { Component } from 'react'
import {Zoom} from 'react-reveal'
import {TextFieldInput, ListField, Button, TextAreaInput, Form} from 'common/Forms.jsx'
import {ErrorMessage} from 'common/Alerts.jsx'
import {isValidJson} from 'common/Common.jsx'
import {sendCustomSms, sendSmsByTemplate, createModificator, deleteModificator, editModificator, createTemplate, editLinkModificator,
  deleteTemplate, editTemplate, createVersion, deleteVersion, editVersion, getModificators, linkModificator, deleteTemplateText, getSystems} from 'api/api.jsx'

const ModalHeader = props =>
  <div className='modal-header'>
    <h5 className='modal-title'>{props.title}{props.subTitle ? <small className='text-muted ml-2'>{props.subTitle}</small> : null}</h5>
    <i className='fas fa-times modal-title p-1' data-role='modal-close' style={{cursor: 'pointer'}} />
  </div>
const ModalBody = props =><div className='modal-body'>{props.children}</div>
const ModalFooter = props =><div className='modal-footer'>{props.children}</div>

export class Modal extends Component {
  constructor(props) {super(props)}
  modalClick = (event) => {if (event.target.dataset.role == 'modal-close') this.toggleModal()}
  toggleModal = () => {
    const {props} = this
    const {rootComponent, modalId} = props
    let newModalsStates = {...rootComponent.state.modals}
    newModalsStates[modalId] = !newModalsStates[modalId]
    rootComponent.setState({...rootComponent.state, modals: newModalsStates})
  }
  componentDidUpdate = () => {
    const {props} = this
    const {rootComponent, modalId} = props
    const show = rootComponent ? rootComponent.state.modals[modalId] : false
    if (!show) {
      document.body.classList.remove('modal-open')
      document.body.style.paddingRight = '0px'
    } else {
      document.body.classList.add('modal-open')
      if (document.body.scrollHeight > window.innerHeight) document.body.style.paddingRight = '18px'
      //document.getElementById(modalId).focus()
    }
  }
  render() {
    const {modalClick, props} = this
    const {children, id, toggle, modalId, rootComponent} = props
    const show = rootComponent ? rootComponent.state.modals[modalId] : false
    return (
      <div>{show ? <div className='modal-backdrop show' /> : null}
        <Zoom bottom>
          <div id={id} className={show ? 'modal fade show' : 'modal'} tabIndex='-1' data-keyboard='true' onClick={modalClick}
            onKeyDown={(event)=>{if (event.key == 'Escape') toggle()}}
            style={show ? {display: 'block', paddingRight: '17px'} : {display: 'none'}}>
            <div className='modal-dialog' role='document'>
              <div className='modal-content'>{children}</div>
            </div>
          </div>
        </Zoom>
      </div>
    )
  }
}

export class SendSmsModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {sendSms: false},
      error: {errorCode: null, errorText: null},
      form: {phoneNumber: '', supplier: '', smsText: ''}
    }
    this.modalId = 'sendSms'
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error} = state
    const {rootComponent} = props
    if (prevState.loading.sendSms == true && state.loading.sendSms == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, sendSms: false},
        loading: {...rootComponent.state.loading, sendSms: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: 'SMS успешно зарегистрирована в системе!'
      })
    }
    if (!prevProps.show && this.props.show)
      this.setState({...this.state,
        form: {phoneNumber: '', supplier: '', smsText: ''},
        error: {errorCode: null, errorText: null}
      })
  }
  handleSearchFormChange = (event) => {
    const {form} = this.state
    switch (event.currentTarget.id) {
    case 'sendSmsPhoneNumber':
      this.setState({...this.state, form: {...form, phoneNumber: event.currentTarget.value}})
      break
    case 'supplier':
      this.setState({...this.state, form: {...form, supplier: event.currentTarget.value}})
      break
    case 'smsText':
      this.setState({...this.state, form: {...form, smsText: event.currentTarget.value}})
      break
    }
  }
  render() {
    const {props, state, handleSearchFormChange, modalId} = this
    const {rootComponent} = props
    const {loading, form, error} = state
    const {errorCode, errorText} = error
    return (
      <Modal rootComponent={rootComponent} modalId={modalId}>
        <ModalHeader title='Отправить SMS'/>
        <ModalBody>
          <Form>
            <TextFieldInput id='sendSmsPhoneNumber' header='Номер телефона' value={form.phoneNumber} changeValue={handleSearchFormChange}
              adaptiveClasses='col-12' disabled={loading.sendSms} isValid={form.phoneNumber && /\+\d{9,}/.test(form.phoneNumber)}
              validationText='Укажите номер телефона в формате +XXXXXXXXXXX (например +71231234567)!'
              clearValue={()=>{this.setState({...this.state, form: {...form, phoneNumber: ''}})}}/>
            <ListField header='Поставщик' id='supplier' value={form.supplier} noSelect isValid={form.supplier} validationText='Выберите поставщика услуги!'
              adaptiveClasses='col-12' valuesList={[{value: 1, verboseValue: "ePochta SMS"}, {value: 3, verboseValue: "IqSms"}, {value: 2, verboseValue: "Тестовый поставщик"}]}
              disabled={loading.sendSms} changeValue={handleSearchFormChange}/>
            <TextAreaInput id='smsText' header='Текст SMS' value={form.smsText} changeValue={handleSearchFormChange} isValid={form.smsText} validationText='Введите текст SMS'
              adaptiveClasses='col-12' rows='4'/>
          </Form>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={()=>{sendCustomSms({phoneNumber: form.phoneNumber, supplierId: form.supplier, text: form.smsText}, this)}}
            loading={loading.sendSms} loadingText='Отправка' disabled={!(form.phoneNumber && /\+\d{9,}/.test(form.phoneNumber) && form.supplier && form.smsText)}>Отправить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class SendSmsByTemplateModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {sendSms: false},
      error: {errorCode: null, errorText: null},
      form: {phoneNumber: '', supplier: ''}
    }
    this.modalId = 'sendSms'
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error} = state
    const {rootComponent} = props
    if (prevState.loading.sendSms == true && state.loading.sendSms == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, sendSms: false},
        loading: {...rootComponent.state.loading, sendSms: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: 'SMS успешно зарегистрирована в системе!'
      })
    }
    if (!prevProps.show && this.props.show)
      this.setState({...this.state,
        form: {phoneNumber: '', supplier: ''},
        error: {errorCode: null, errorText: null}
      })
  }
  handleSearchFormChange = (event) => {
    const {form} = this.state
    switch (event.currentTarget.id) {
    case 'sendSmsPhoneNumber':
      this.setState({...this.state, form: {...form, phoneNumber: event.currentTarget.value}})
      break
    case 'supplier':
      this.setState({...this.state, form: {...form, supplier: event.currentTarget.value}})
      break
    }
  }
  render() {
    const {props, state, handleSearchFormChange, modalId} = this
    const {rootComponent, smsParamsToSend} = props
    const {loading, form, error} = state
    const {errorCode, errorText} = error
    return (
      <Modal rootComponent={rootComponent} modalId={modalId}>
        <ModalHeader title='Отправить SMS'/>
        <ModalBody>
          <Form>
            <div className='col-12'>
              Данные для SMS (шаблон сообщения и данные для шаблона) будут взяты соответственно из версии и модификатора шаблона.
            </div>
            <TextFieldInput id='sendSmsPhoneNumber' header='Номер телефона' value={form.phoneNumber} changeValue={handleSearchFormChange}
              adaptiveClasses='col-12' disabled={loading.sendSms} isValid={form.phoneNumber && /\+\d{9,}/.test(form.phoneNumber)}
              validationText='Укажите номер телефона в формате +XXXXXXXXXXX (например +71231234567)!'
              clearValue={()=>{this.setState({...this.state, form: {...form, phoneNumber: ''}})}}/>
            <ListField header='Поставщик' id='supplier' value={form.supplier} noSelect isValid={form.supplier} validationText='Выберите поставщика услуги!'
              adaptiveClasses='col-12' valuesList={[{value: 1, verboseValue: "ePochta SMS"}, {value: 3, verboseValue: "IqSms"}, {value: 2, verboseValue: "Тестовый поставщик"}]}
              disabled={loading.sendSms} changeValue={handleSearchFormChange}/>
          </Form>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={()=>{sendSmsByTemplate({...smsParamsToSend, phoneNumber: form.phoneNumber, supplierId: form.supplier}, this)}}
            loading={loading.sendSms} loadingText='Отправка' disabled={!(form.phoneNumber && /\+\d{9,}/.test(form.phoneNumber) && form.supplier)}>Отправить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class CreateTemplateModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      systems: [],
      loading: {sendSms: false, getSystems: false},
      error: {errorCode: null, errorText: null},
      form: {name: '', systemId: '', description: '', id: ''}
    }
    this.modalId = 'createTemplate'
  }
  componentDidMount = () => {
    getSystems(this)
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error} = state
    const {rootComponent} = props
    if (prevState.loading.createTemplate == true && state.loading.createTemplate == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, createTemplate: false},
        loading: {...rootComponent.state.loading, createTemplate: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: 'Шаблон успешно создан!'
      })
    }
    if (!prevProps.show && this.props.show)
      this.setState({...this.state,
        form: {name: '', systemId: '', description: '', id: ''},
        error: {errorCode: null, errorText: null}
      })
  }
  handleSearchFormChange = (event) => {
    const {form} = this.state
    switch (event.currentTarget.id) {
    case 'templateName':
      this.setState({...this.state, form: {...form, name: event.currentTarget.value}})
      break
    case 'systemId':
      this.setState({...this.state, form: {...form, systemId: event.currentTarget.value}})
      break
    case 'description':
      this.setState({...this.state, form: {...form, description: event.currentTarget.value}})
      break
    case 'id':
      this.setState({...this.state, form: {...form, id: event.currentTarget.value}})
      break
    }
  }
  render() {
    const {props, state, handleSearchFormChange, modalId} = this
    const {rootComponent} = props
    const {loading, form, error, systems} = state
    const {errorCode, errorText} = error
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Создать новый шаблон'/>
        <ModalBody>
          <Form>
            <TextFieldInput id='id' header='Идентификатор шаблона' maxLength='32' value={form.id} changeValue={handleSearchFormChange} helpText='Допускаются латинские буквы, цифры, знак подчёркивания и тире'
              adaptiveClasses='col-12' disabled={loading.createTemplate} isValid={form.id && /^[A-Za-z0-9]+[A-Z-a-z0-9-_]*[A-Za-z0-9]+/.test(form.id)} validationText='Идентификатор не указан или некорректен!'
              clearValue={()=>{this.setState({...this.state, form: {...form, id: ''}})}}/>
            <TextFieldInput id='templateName' header='Название шаблона' maxLength='50' value={form.name} changeValue={handleSearchFormChange}
              adaptiveClasses='col-12' disabled={loading.createTemplate} isValid={form.name} validationText='Укажите название шаблона!'
              clearValue={()=>{this.setState({...this.state, form: {...form, name: ''}})}}/>
            <ListField header='Система' id='systemId' value={form.systemId} noSelect isValid={form.systemId} validationText='Выберите систему!'
              adaptiveClasses='col-12' valuesList={systems.map((valueItem) => ({value: valueItem.id, verboseValue: valueItem.name}))}
              disabled={loading.createTemplate} changeValue={handleSearchFormChange}/>
            <TextAreaInput id='description' header='Описание' max='256' value={form.description} changeValue={handleSearchFormChange} isValid adaptiveClasses='col-12' rows='4'/>
          </Form>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={()=>{createTemplate(form, this)}} loading={loading.sendSms} loadingText='Создание'
            disabled={!(form.name && form.systemId)}>Создать</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class DeleteTemplateModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {deleteTemplate: false},
      error: {errorCode: null, errorText: null}
    }
    this.modalId = 'deleteTemplate'
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error} = state
    const {rootComponent, templateId} = props
    if (prevState.loading.deleteTemplate == true && state.loading.deleteTemplate == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        isDeleted: true,
        modals: {...rootComponent.state.modals, deleteTemplate: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: <span>Шаблон <span className='font-weight-bold'>{templateId}</span> успешно удалён!</span>
      })
    }
  }
  render() {
    const {props, state, modalId} = this
    const {loading, error} = state
    const {errorCode, errorText} = error
    const {rootComponent, templateId} = props
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Удалить шаблон'/>
        <ModalBody>
          <div className='mb-3'>Удалить шаблон {templateId}?</div>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={() => {deleteTemplate(templateId, this)}} loading={loading.deleteTemplate} loadingText='Удаление'>Удалить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class EditTemplateModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {editTemplate: false},
      error: {errorCode: null, errorText: null}
    }
    this.modalId = 'editTemplate'
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error} = state
    const {rootComponent, templateId} = props
    if (prevState.loading.editTemplate == true && state.loading.editTemplate == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, editTemplate: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: <span>Шаблон <span className='font-weight-bold'>{templateId}</span> успешно обновлён!</span>
      })
    }
  }
  render() {
    const {props, state, modalId} = this
    const {loading, error} = state
    const {errorCode, errorText} = error
    const {rootComponent, templateInfo} = props
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Сохранить изменения'/>
        <ModalBody>
          <p>Сохранить изменения в шаблоне <b>{templateInfo.id}</b>?</p>
          <p className='mb-3'>Параметры шаблона, которые будут применены:</p>
          <ul>
            <li>Название шаблона: <b>{templateInfo.name}</b></li>
            <li>Описание шаблона: <b>{templateInfo.description}</b></li>
            <li>ID системы-владельца: <b>{templateInfo.systemId}</b></li>
          </ul>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={() => {editTemplate({id: templateInfo.id, name: templateInfo.name, systemId: templateInfo.systemId, description: templateInfo.description}, this)}} loading={loading.editTemplate} loadingText='Удаление'>Сохранить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class CreateVersionModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {createVersion: false},
      error: {errorCode: null, errorText: null},
      form: {versionId: '', description: '', jsonExample: '', templateText: '', templateId: props.templateId, scopeId: 'default'}
    }
    this.modalId = 'createVersion'
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {rootComponent} = props
    const {error} = state
    if (!prevProps.show && this.props.show)
      this.setState({...this.state,
        form: {versionId: '', description: '', jsonExample: '', templateText: '', templateId: props.templateId, scopeId: 'default'},
        error: {errorCode: null, errorText: null}
      })
    if (prevState.loading.createVersion == true && state.loading.createVersion == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, createVersion: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: 'Версия успешно создана!'
      })
    }
  }
  handleSearchFormChange = (event) => {
    const {form} = this.state
    switch (event.currentTarget.id) {
    case 'versionId':
      this.setState({...this.state, form: {...form, versionId: event.currentTarget.value}})
      break
    case 'versionDescription':
      this.setState({...this.state, form: {...form, description: event.currentTarget.value}})
      break
    case 'versionData':
      this.setState({...this.state, form: {...form, jsonExample: event.currentTarget.value}})
      break
    case 'versionText':
      this.setState({...this.state, form: {...form, templateText: event.currentTarget.value}})
      break
    }
  }
  render() {
    const {props, state, handleSearchFormChange, modalId} = this
    const {loading, form, error} = state
    const {errorCode, errorText} = error
    const {rootComponent} = props
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Создать версию шаблона'/>
        <ModalBody>
          <Form>
            <TextFieldInput id='versionId' header='ID версии' value={form.versionId} changeValue={handleSearchFormChange}
              adaptiveClasses='col-12' isValid={form.versionId} validationText='Укажите ID версии!'
              clearValue={()=>{this.setState({...this.state, form: {...form, description: ''}})}}/>
            <TextFieldInput id='versionDescription' header='Описание версии' value={form.description} changeValue={handleSearchFormChange}
              adaptiveClasses='col-12' isValid={form.description} validationText='Заполните описание!'
              clearValue={()=>{this.setState({...this.state, form: {...form, description: ''}})}}/>
            <TextAreaInput id='versionData' header='Пример данных для формирования SMS (JSON)' value={form.jsonExample} changeValue={handleSearchFormChange} adaptiveClasses='col-12' 
              monospaceFont rows='8' isValid={isValidJson(form.jsonExample)} validationText='Введённый JSON невалиден!'/>
            <TextAreaInput id='versionText' header='Шаблон SMS' adaptiveClasses='col-12' value={form.templateText} changeValue={handleSearchFormChange} monospaceFont rows='3'
              isValid={form.templateText} validationText='Введите шаблон SMS!'/>
          </Form>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={()=>{createVersion(form, this)}} loading={loading.createVersion} loadingText='Создание' 
            disabled={!(form.description && form.jsonExample && form.templateText && form.versionId && isValidJson(form.jsonExample) == true)}>Создать</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class EditVersionModal extends Component {
  constructor(props) {
    super(props)
    this.modalId = 'editVersion'
    this.state = {
      loading: {},
      error: {errorCode: null, errorText: null}
    }
    this.state.loading[this.modalId] = false
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error} = state
    const {rootComponent, versionInfo} = props
    if (prevState.loading.editVersion == true && state.loading.editVersion == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, editVersion: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: <span>Версия <span className='font-weight-bold'>{versionInfo.id}</span> успешно обновлена!</span>
      })
    }
  }
  render() {
    const {props, state, modalId} = this
    const {loading, error} = state
    const {errorCode, errorText} = error
    const {rootComponent, versionInfo} = props
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Сохранить изменения'/>
        <ModalBody>
          <p>Сохранить изменения в версии <b>{versionInfo.id}</b>?</p>
          <p className='mb-3'>Новые параметры версии:</p>
          <ul>
            <li>Описание версии: <b>{versionInfo.description}</b></li>
            <li>Пример данных: <b>{versionInfo.dataJson}</b></li>
          </ul>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' 
          action={() => {editVersion({versionId: versionInfo.id, templateId: versionInfo.templateId, scopeId: versionInfo.scopeId, description: versionInfo.description, templateText: versionInfo.templateText, jsonExample: versionInfo.dataJson}, this)}} loading={loading.editTemplate} loadingText='Удаление'>Сохранить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class DeleteVersionModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {deleteVersion: false},
      error: {errorCode: null, errorText: null}
    }
    this.modalId = 'deleteVersion'
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error} = state
    const {rootComponent, templateId} = props
    if (prevState.loading.deleteVersion == true && state.loading.deleteVersion == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        isDeleted: true,
        modals: {...rootComponent.state.modals, deleteVersion: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: <span>Версия <span className='font-weight-bold'>{templateId}</span> успешно удалена!</span>
      })
    }
  }
  render() {
    const {props, state, modalId} = this
    const {loading, error} = state
    const {errorCode, errorText} = error
    const {rootComponent, versionToDelete} = props
    const {versionId, scopeId, templateId} = versionToDelete
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Удалить версию'/>
        <ModalBody>
          <div className='mb-3'>Удалить версию {versionId}?</div>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={() => {deleteVersion(templateId, versionId, scopeId, this)}} loading={loading.deleteVersion} loadingText='Удаление'>Удалить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class CreateModificatorModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {createModificator: false},
      error: {errorCode: null, errorText: null},
      form: {name: '', id: ''}
    }
    this.modalId = 'createModificator'
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error, loading, form} = state
    const {rootComponent} = props
    if (!prevProps.show && props.show) {
      this.setState({...state, form: {id: '', name: ''}, error: {errorCode: null, errorText: null}})
    }
    if (prevState.loading.createModificator == true && loading.createModificator == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, createModificator: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: <span>Модификатор <span className='font-weight-bold'>{form.id}</span> (<span className='font-weight-bold'>{form.name}</span>) успешно добавлен!</span>
      })
    }
  }
  handleSearchFormChange = (event) => {
    const {form} = this.state
    switch (event.currentTarget.id) {
    case 'modificatorName':
      this.setState({...this.state, form: {...form, name: event.currentTarget.value}})
      break
    case 'modificatorId':
      this.setState({...this.state, form: {...form, id: event.currentTarget.value}})
      break
    }
  }
  render() {
    const {props, state, handleSearchFormChange, modalId} = this
    const {loading, form, error} = state
    const {errorCode, errorText} = error
    const {rootComponent} = props
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Создать модификатор'/>
        <ModalBody>
          <Form>
            <TextFieldInput id='modificatorId' header='ID модификатора' value={form.id} changeValue={handleSearchFormChange}
              adaptiveClasses='col-12' isValid={form.id} validationText='Задайте ID!'
              clearValue={()=>{this.setState({...this.state, form: {...form, id: ''}})}}/>
            <TextFieldInput id='modificatorName' header='Название модификатора' value={form.name} changeValue={handleSearchFormChange}
              adaptiveClasses='col-12' isValid={form.name} validationText='Заполните описание!'
              clearValue={()=>{this.setState({...this.state, form: {...form, name: ''}})}}/>
          </Form>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={() => {createModificator({id: form.id, name: form.name}, this)}} loading={loading.createModificator} loadingText='Создание' disabled={!(form.name && form.id)}>Создать</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class EditModificatorModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {editModificator: false},
      error: {errorCode: null, errorText: null},
      form: {name: ''}
    }
    this.modalId = 'editModificator'
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error, loading, form} = state
    const {rootComponent, modificatorId, modificatorName} = props
    if (!prevProps.show && props.show) {
      this.setState({...state, form: {name: modificatorName}, error: {errorCode: null, errorText: null}})
    }
    if (prevState.loading.editModificator == true && loading.editModificator == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, editModificator: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: <span>Модификатор <span className='font-weight-bold'>{modificatorId}</span> (<span className='font-weight-bold'>{form.name}</span>) успешно изменён!</span>
      })
    }
  }
  handleSearchFormChange = (event) => {
    const {form} = this.state
    switch (event.currentTarget.id) {
    case 'modificatorName':
      this.setState({...this.state, form: {...form, name: event.currentTarget.value}})
      break
    }
  }
  render() {
    const {props, state, handleSearchFormChange, modalId} = this
    const {loading, form, error} = state
    const {errorCode, errorText} = error
    const {rootComponent, modificatorId} = props
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Изменить модификатор'/>
        <ModalBody>
          <Form>
            <TextFieldInput id='modificatorName' header='Название модификатора' value={form.name} changeValue={handleSearchFormChange}
              adaptiveClasses='col-12' isValid={form.name} validationText='Заполните название!'
              clearValue={()=>{this.setState({...this.state, form: {...form, name: ''}})}}/>
          </Form>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={() => {editModificator({id: modificatorId, name: form.name}, this)}} loading={loading.editModificator}
            loadingText='Изменить' disabled={!form.name}>Изменить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class DeleteModificatorModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {deleteModificator: false},
      error: {errorCode: null, errorText: null}
    }
    this.modalId = 'deleteModificator'
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error} = state
    const {rootComponent, modificatorId} = props
    if (prevState.loading.deleteModificator == true && state.loading.deleteModificator == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, deleteModificator: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: <span>Модификатор <span className='font-weight-bold'>{modificatorId}</span> успешно удалён!</span>
      })
    }
  }
  render() {
    const {props, state, modalId} = this
    const {loading, error} = state
    const {errorCode, errorText} = error
    const {rootComponent, modificatorId} = props
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Удалить модификатор'/>
        <ModalBody>
          Удалить модификатор {modificatorId}?
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={() => {deleteModificator(modificatorId, this)}} loading={loading.deleteModificator} loadingText='Удаление'>Удалить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class EditSmsTemplateModal extends Component {
  constructor(props) {
    super(props)
    this.modalId = 'editSmsTemplate'
    this.state = {
      form: {templateText: ''},
      initialForm : {templateText: ''},
      loading: {editSmsTemplate: false},
      error: {errorCode: null, errorText: null}
    }
    this.state.loading[this.modalId] = false
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error} = state
    const {rootComponent, textToEdit} = props
    if (!prevProps.show && props.show) {
      this.setState({...state, initialForm : {templateText: textToEdit.templateText}, form: {templateText: textToEdit.templateText}, error: {errorCode: null, errorText: null}})
    }
    if (prevState.loading.editSmsTemplate == true && state.loading.editSmsTemplate == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, editSmsTemplate: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: <span>Текст шаблона SMS модификатора <span className='font-weight-bold'>{textToEdit.scopeId}</span> успешно обновлен!</span>
      })
    }
  }
  handleSearchFormChange = (event) => {
    const {form} = this.state
    switch (event.currentTarget.id) {
    case 'versionText':
      this.setState({...this.state, form: {...form, templateText: event.currentTarget.value}})
      break
    }
  }
  render() {
    const {props, state, modalId, handleSearchFormChange} = this
    const {loading, error, form, initialForm} = state
    const {errorCode, errorText} = error
    const {rootComponent, textToEdit} = props
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Изменить текст SMS'/>
        <ModalBody>
          <Form>
            <div className='col-12'>ID Шаблона: <b>{textToEdit.templateId}</b></div>
            <div className='col-12'>ID версии шаблона: <b>{textToEdit.versionId}</b></div>
            <div className='col-12 mb-3'>ID модификатора: <b>{textToEdit.scopeId}</b></div>
            <TextAreaInput id='versionText' header='Шаблон SMS' adaptiveClasses='col-12' value={form.templateText} changeValue={handleSearchFormChange} 
              monospaceFont rows='3' isValid={form.templateText} isEdited={form.templateText != initialForm.templateText} validationText='Введите шаблон SMS!'/>
          </Form>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' disabled={form.templateText == initialForm.templateText || !form.templateText}
            action={() => {editLinkModificator({versionId: textToEdit.versionId, templateId: textToEdit.templateId, scopeId: textToEdit.scopeId, templateVersionText: form.templateText}, this)}} loading={loading.editTemplate} loadingText='Удаление'>Сохранить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class LinkModificatorModal extends Component {
  constructor(props) {
    super(props)
    this.modalId = 'linkModificator'
    this.state = {
      modificatorsList: [],
      form: {templateText: '', modificatorId: ''},
      loading: {},
      error: {errorCode: null, errorText: null}
    }
    this.state.loading[this.modalId] = false
  }
  componentDidMount = () => {getModificators(this)}
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error, form} = state
    const {rootComponent} = props
    if (!prevProps.show && props.show) {
      this.setState({...state, form: {templateText: '', modificatorId: ''}, error: {errorCode: null, errorText: null}})
    }
    if (prevState.loading.linkModificator == true && state.loading.linkModificator == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, linkModificator: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: <span>Модификатор <span className='font-weight-bold'>{form.modificatorId}</span> успешно привязан!</span>
      })
    }
  }
  handleSearchFormChange = (event) => {
    const {form} = this.state
    switch (event.currentTarget.id) {
    case 'versionText':
      this.setState({...this.state, form: {...form, templateText: event.currentTarget.value}})
      break
    case 'modificatorId':
      this.setState({...this.state, form: {...form, modificatorId: event.currentTarget.value}})
      break
    }
  }
  render() {
    const {props, state, modalId, handleSearchFormChange} = this
    const {loading, error, form, modificatorsList} = state
    const {errorCode, errorText} = error
    const {rootComponent, templateId, versionId} = props
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Привязать модификатор'/>
        <ModalBody>
          <Form>
            <div className='col-12'>ID Шаблона: <b>{templateId}</b></div>
            <div className='col-12 mb-3'>ID версии шаблона: <b>{versionId}</b></div>
            <ListField header='Модификатор' id='modificatorId' value={form.modificatorId} noSelect isValid={form.modificatorId} validationText='Выберите модификатор!'
              adaptiveClasses='col-12' valuesList={modificatorsList.map((valueItem) => ({value: valueItem.id, verboseValue: valueItem.name}))}
              disabled={loading.createTemplate} changeValue={handleSearchFormChange}/>
            <TextAreaInput id='versionText' header='Шаблон SMS' adaptiveClasses='col-12' value={form.templateText} changeValue={handleSearchFormChange} 
              monospaceFont rows='3' isValid={form.templateText} validationText='Введите шаблон SMS!'/>
          </Form>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' disabled={!form.templateText || !form.modificatorId}
            action={() => {linkModificator({templateId: templateId, versionId: versionId, templateVersionText: form.templateText, scopeId: form.modificatorId}, this)}} loading={loading.linkModificator} loadingText='Привязка'>Сохранить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export class DeleteTemplateTextModal extends Component {
  constructor(props) {
    super(props)
    this.state = {
      loading: {deleteTemplateText: false},
      error: {errorCode: null, errorText: null}
    }
    this.modalId = 'deleteTemplateText'
  }
  componentDidUpdate = (prevProps, prevState) => {
    const {state, props} = this
    const {error} = state
    const {rootComponent, modificatorId} = props
    if (!prevProps.show && props.show) {this.setState({...state, error: {errorCode: null, errorText: null}})}
    if (prevState.loading.deleteTemplateText == true && state.loading.deleteTemplateText == false && !error.errorCode) {
      rootComponent.setState({...rootComponent.state,
        needReload: true,
        modals: {...rootComponent.state.modals, deleteTemplateText: false},
        error: {errorCode: error.errorCode, errorText: error.errorText},
        success: <span>Связь модификатора<span className='font-weight-bold'>{modificatorId}</span> успешно удалена!</span>
      })
    }
  }
  render() {
    const {props, state, modalId} = this
    const {loading, error} = state
    const {errorCode, errorText} = error
    const {rootComponent, modificatorId, textToDelete} = props
    return (
      <Modal modalId={modalId} rootComponent={rootComponent}>
        <ModalHeader title='Удалить связь'/>
        <ModalBody>
          <div className='mb-3'>Удалить связь модификатора {modificatorId}?</div>
          {errorCode ? <ErrorMessage closeAction={()=>{this.setState({...this.state, error: {errorCode: null, errorText: null}})}}>{errorText}</ErrorMessage> : null}
        </ModalBody>
        <ModalFooter>
          <Button fixedWidth='8rem' action={() => {deleteTemplateText(textToDelete, this)}} loading={loading.deleteModificator} loadingText='Удаление'>Удалить</Button>
          <Button fixedWidth='8rem' role='modal-close' color='secondary'>Закрыть</Button>
        </ModalFooter>
      </Modal>
    )
  }
}

export default Modal