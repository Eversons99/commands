const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value

async function getBoardsHost() {
    try {
        const sourceHost = document.getElementById('select-olt').value
        let hostSlots = await fetch(`https://nmt.nmultifibra.com.br/files/hosts?olt=${sourceHost}`)
        hostSlots = await hostSlots.json()
    
        if (hostSlots.message == 'Host not Found') {
            return alert(`Ocorreu um erro ao buscar as informações da ${sourceHost} no NMT`)
        }
        fillElementsOptions(hostSlots)
    } catch (error) {
        return alert(`Ocorreu um erro ao consultar o NMT (Verifique a rede). Error ${error}`)
    }
}

function fillElementsOptions(slots) {
    const slotSelectElement = document.getElementById('select-slot')
    const portSelectElement = document.getElementById('select-port')
    let counterPorts = 0

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

function setIdentificator() {
    const identificatorTab = Date.now()
    window.sessionStorage.setItem('tabId', identificatorTab)
}

async function searchOnts() {
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
    
    if (!sourceHost || !sourceSlot || !sourcePort) return alert("ATENÇÃO: Preencha o F/S/P!")

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

    const ontsRequest = await fetch('http://10.0.30.241:8000/generator/search_onts', requestOptions)
    const responsOfontsRequest = await ontsRequest.json()

    if (responsOfontsRequest.save_maintence_info.error == true) {
        const messageError = responsOfontsRequest.message
        return window.location = `http://10.0.30.241:8000/generator/render_error_page?message=${messageError}`
    }

    return window.location = `http://10.0.30.241:8000/generator/render_onts_table?tab_id=${tabId}` 

}

async function searchOntsSms() {
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
    
    if (!sourceHost || !sourceSlot || !sourcePort) return alert("ATENÇÃO: Preencha o F/S/P!")

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
    
    const ontsRequest = await fetch('http://10.0.30.241:8000/sms/search_onts', requestOptions)
    const responsOfontsRequest = await ontsRequest.json()

    if (responsOfontsRequest.error == true) {
        const messageError = responsOfontsRequest.message
        return window.location = `http://10.0.30.241:8000/sms/render_error_page?message=${messageError}`
    }

    return window.location = `http://10.0.30.241:8000/sms/render_onts_table?tab_id=${tabId}` 
}

function getIdentificator() {
    const identificatorTab = window.sessionStorage.getItem('tabId')
    return identificatorTab
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

async function generateCommands() {
    const allDevices = document.querySelectorAll('#cbx-single-item')
    const idDevicesSelecteds = []

    allDevices.forEach((device) => {
        if (device.checked) {
            const deviceId = device.parentNode.parentNode.children[1].innerHTML
            idDevicesSelecteds.push(Number(deviceId))
        }
    })

    if (idDevicesSelecteds.length == 0) return alert('Selecione ao menos um dispositivo')

    const destinationHost = document.getElementById('select-olt').value
    const destinationSlot = document.getElementById('select-slot').value
    const destinationPort = document.getElementById('select-port').value 
    const fileName = document.getElementById('file-name').value
    const tabId = getIdentificator()
    const destinationGpon = {
        'host': destinationHost,
        'gpon': `0/${destinationSlot}/${destinationPort}`
    }

    if (!destinationHost || !destinationSlot || !destinationPort) {
        return alert('Preecha o F/S/P para prosseguir')
    } else if (!fileName) {
        return alert('Digite um nome para o seu arquivo para prosseguir')
    }

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            tabId,
            destinationGpon,
            fileName,
            idDevicesSelecteds
        })
    }

    let getCommands = await fetch('http://10.0.30.241:8000/generator/get_commands', requestOptions)
    getCommands = await getCommands.json()
    
    if (getCommands.error) {
        messageError =  getCommands.message
        return window.location = `http://10.0.30.241:8000/generator/render_error_page?message=${messageError}`
    }
    return window.location = `http://10.0.30.241:8000/generator/render_page_commands?tab_id=${tabId}` 
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

    let getContacts = await fetch('http://10.0.30.241:8000/sms/get_contacts', requestOptions)
    getContacts = await getContacts.json()
    
    if (getContacts.error) {
        messageError =  getContacts.message
        return window.location = `http://10.0.30.241:8000/sms/render_error_page?message=${messageError}`
    }
    return window.location = `http://10.0.30.241:8000/sms/render_contacts_page?tab_id=${tabId}` 
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

    const createRuptureRequest = await fetch('http://10.0.30.241:8000/sms/create_rupture', requestOptions)
    const ruptureResponse = await createRuptureRequest.json()

    if (ruptureResponse.error) {
        messageError =  ruptureResponse.message
        return window.location = `http://10.0.30.241:8000/sms/render_error_page?message=${messageError}`
    }
    return window.location = `http://10.0.30.241:8000/sms/render_rupture_page?tab_id=${tabId}` 
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

    const sendSmsRequest = await fetch('http://10.0.30.241:8000/sms/send_sms', requestOptions)
    const smsResponse = await sendSmsRequest.json()

    if (smsResponse.error) {
        messageError =  smsResponse.message
        return window.location = `http://10.0.30.241:8000/sms/render_error_page?message=${messageError}`
    }
    return window.location = `http://10.0.30.241:8000/sms/render_sms_result_page?tab_id=${tabId}` 
}