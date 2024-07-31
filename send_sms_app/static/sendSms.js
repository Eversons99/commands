const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value

function loadingAnimation(active) {
    const divLoader = document.getElementsByClassName('modal-loader')[0]
    const body = document.getElementsByTagName('body')[0]
    
    if (active) {
        divLoader.style.display = "flex"
        body.classList.add('disable-scroll')
        window.scroll(0, 0)
    } else {
        divLoader.style.display = "none"
        body.classList.remove('disable-scroll')
    }
}

function setIdentificator() {
    const identificatorTab = Date.now()
    window.sessionStorage.setItem('tabId', identificatorTab)
}

function getIdentificator() {
    const identificatorTab = window.sessionStorage.getItem('tabId')
    return identificatorTab
}

function markSelectedItem() {
    const singleSelect = document.querySelectorAll('#cbx-single-item')
    const selectAll = document.querySelectorAll('#cbx-select-all')

    singleSelect.forEach( input => {
        if (selectAll.checked || input.checked) {
            input.parentElement.parentElement.style.color = 'rgb(64, 76, 87)'
            input.parentElement.parentElement.style.background = 'rgb(222, 222, 222)'
        } else {
            input.parentElement.parentElement.style.color = 'black'
            input.parentElement.parentElement.style.background = 'white'
        }
    })
}

function selectAllDevices() {
    const checkboxSelectAll = document.getElementById('cbx-select-all')
    const checkboxesSingleItems = document.querySelectorAll('#cbx-single-item')

    checkboxesSingleItems.forEach((singleCheckbox) => {
        if (checkboxSelectAll.checked) {
            singleCheckbox.checked = true
        } else {
            singleCheckbox.checked = false
        }
    })

    markSelectedItem()
}

async function searchOntsSms() {
    loadingAnimation(true)
    setIdentificator()
    const sourceHost = document.getElementById('select-olt').value
    const sourceSlot = document.getElementById('select-slot').value
    const sourcePort = document.getElementById('select-port').value
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
    const tabId = getIdentificator()
    const sourceGpon = {
        'host':  sourceHost,
        'gpon': `0/${sourceSlot}/${sourcePort}`
    }
    
    if (!sourceHost || !sourceSlot || !sourcePort) {
        loadingAnimation(false)
        return alert("ATENÇÃO: Preencha o F/S/P!")
    }
    const requestOptions = {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            tabId,
            sourceGpon
        })
    }
    
    const ontsRequest = await fetch('http://commands.nmultifibra.com.br/dk/maintenance/sms/search_onts', requestOptions)
    const responsOfontsRequest = await ontsRequest.json()
    console.log(responsOfontsRequest)
    if (responsOfontsRequest.error == true) {
        const messageError = responsOfontsRequest.message
        return window.location = `http://commands.nmultifibra.com.br/dk/maintenance/sms/render_error_page?message=${messageError}`
    }

    return window.location = `http://commands.nmultifibra.com.br/dk/maintenance/sms/render_onts_table?tab_id=${tabId}` 
}

async function getNumbersToSendSms() {
    const allDevices = document.querySelectorAll('#cbx-single-item')
    const serialNumbers = []

    allDevices.forEach((device) => {
        if (device.checked) {
            const serialNumber = device.parentNode.parentNode.children[2].innerHTML
            serialNumbers.push(serialNumber)
        }
    })

    if (serialNumbers.length == 0) return alert('Selecione ao menos um dispositivo')

    const tabId = getIdentificator()

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            tabId,
            serialNumbers
        })
    }

    let getContacts = await fetch('http://commands.nmultifibra.com.br/dk/maintenance/sms/get_contacts', requestOptions)
    getContacts = await getContacts.json()
    
    if (getContacts.error) {
        messageError =  getContacts.message
        return window.location = `http://commands.nmultifibra.com.br/dk/maintenance/sms/render_error_page?message=${messageError}`
    }
    return window.location = `http://commands.nmultifibra.com.br/dk/maintenance/sms/render_contacts_page?tab_id=${tabId}` 
}

async function createRupture() {
    const previsao = document.getElementById('input-previsao').value
    const tipoRompimento = document.getElementById('input-tipo').value
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
    const tabId = getIdentificator()

    if (!previsao || !tipoRompimento) return alert("ATENÇÃO: Informe a Previsão e o tipo do rompimento!")

    const requestOptions = {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            tabId,
            previsao,
            tipoRompimento
        })
    }

    const createRuptureRequest = await fetch('http://commands.nmultifibra.com.br/dk/maintenance/sms/create_rupture', requestOptions)
    const ruptureResponse = await createRuptureRequest.json()

    if (ruptureResponse.error) {
        messageError =  ruptureResponse.message
        return window.location = `http://commands.nmultifibra.com.br/dk/maintenance/sms/render_error_page?message=${messageError}`
    }
    return window.location = `http://commands.nmultifibra.com.br/dk/maintenance/sms/render_rupture_page?tab_id=${tabId}` 
}

async function sendSms() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
    const tabId = getIdentificator()

    const requestOptions = {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            tabId,
        })
    }

    const sendSmsRequest = await fetch('http://commands.nmultifibra.com.br/dk/maintenance/sms/send_sms', requestOptions)
    const smsResponse = await sendSmsRequest.json()

    if (smsResponse.error) {
        messageError =  smsResponse.message
        return window.location = `http://commands.nmultifibra.com.br/dk/maintenance/sms/render_error_page?message=${messageError}`
    }
    return window.location = `http://commands.nmultifibra.com.br/dk/maintenance/sms/render_sms_result_page?tab_id=${tabId}` 
}

async function getBoardsHost() {
    try {
        loadingAnimation(true)
        const sourceHost = document.getElementById('select-olt').value
        let hostSlots = await fetch(`https://nmt.nmultifibra.com.br/files/hosts?olt=${sourceHost}`)
        hostSlots = await hostSlots.json()
    
        if (hostSlots.message == 'Host not Found') {
            loadingAnimation(false)
            return alert(`Ocorreu um erro ao buscar as informações da ${sourceHost} no NMT`)
        }
        fillElementsOptions(hostSlots)
        loadingAnimation(false)
    } catch (error) {
        loadingAnimation(false)
        return alert(`Ocorreu um erro ao consultar o NMT (Verifique a rede). Error ${error}`)
    }
}

async function fillElementsOptions(slots) {
    const slotSelectElement = document.getElementById('select-slot')
    const portSelectElement = document.getElementById('select-port')
    let counterPorts = 0

    slotSelectElement.textContent = ''
    portSelectElement.textContent = ''
    slotSelectElement.append(document.createElement('option'))
    portSelectElement.append(document.createElement('option'))

    slots.forEach((slot) => {
        const optionPortElement = document.createElement('option')
        const currentPortValue = slot.split('/')[1]
        optionPortElement.textContent = currentPortValue
        slotSelectElement.append(optionPortElement)
    })

    while (counterPorts < 16) {
        const optionPortElement = document.createElement('option')
        optionPortElement.textContent = counterPorts
        portSelectElement.append(optionPortElement)
        counterPorts++
    }
}