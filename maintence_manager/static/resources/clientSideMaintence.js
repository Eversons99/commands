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

    const ontsRequest = await fetch('http://localhost:8000/generator/search_onts', requestOptions)
    const responsOfontsRequest = await ontsRequest.json()
    
    if (responsOfontsRequest.error == true) {
        const messageError = responsOfontsRequest.message
        return window.location = `http://localhost:8000/generator/render_error_page?message=${messageError}`
    }

    return window.location = `http://localhost:8000/generator/render_onts_table?tab_id=${tabId}` 
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

    let getCommands = await fetch('http://localhost:8000/generator/get_commands', requestOptions)
    getCommands = await getCommands.json()
    
    if (getCommands.error) {
        messageError =  getCommands.message
        return window.location = `http://localhost:8000/generator/render_error_page?message=${messageError}`
    }
    return window.location = `http://localhost:8000/generator/render_page_commands?tab_id=${tabId}` 
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

function resultsButton(e) {
    const interfaceDiv = document.getElementById('interface-results')
    const globalDiv = document.getElementById('global-results')
    const deleteDiv = document.getElementById('delete-results')

    const interfaceButton = document.getElementById('interface-button')
    const globalButton = document.getElementById('global-button')
    const deleteButton = document.getElementById('delete-button')

    if (e.target.id == 'interface-button') {
        interfaceDiv.setAttribute('class', 'active-result')
        globalDiv.setAttribute('class', 'inactive-result')
        deleteDiv.setAttribute('class', 'inactive-result')
        
        interfaceButton.setAttribute('class', 'active-btn')
        globalButton.setAttribute('class', 'inactive-btn')
        deleteButton.setAttribute('class', 'inactive-btn')
    }

    if (e.target.id == 'global-button') {
        globalDiv.setAttribute('class', 'active-result')
        interfaceDiv.setAttribute('class', 'inactive-result')
        deleteDiv.setAttribute('class', 'inactive-result')

        globalButton.setAttribute('class', 'active-btn')
        interfaceButton.setAttribute('class', 'inactive-btn')
        deleteButton.setAttribute('class', 'inactive-btn')
    }
    if (e.target.id == 'delete-button') {
        deleteDiv.setAttribute('class', 'active-result')
        globalDiv.setAttribute('class', 'inactive-result')
        interfaceDiv.setAttribute('class', 'inactive-result')

        deleteButton.setAttribute('class', 'active-btn')
        globalButton.setAttribute('class', 'inactive-btn')
        interfaceButton.setAttribute('class', 'inactive-btn')
    }
}
