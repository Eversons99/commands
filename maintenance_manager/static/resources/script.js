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

async function searchOnts(operationMode) {
    setIdentificator()
    loadingAnimation(true)
    const baseUrl = "http://10.0.30.157:8000" + (operationMode == 'generator' ? '/generator' : '/attenuator')
    const sourceHost = document.getElementById('select-olt').value
    const sourceSlot = document.getElementById('select-slot').value
    const sourcePort = document.getElementById('select-port').value
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

    const ontsRequest = await fetch(`${baseUrl}/search_onts_via_snmp`, requestOptions)
    const responseRequest = await ontsRequest.json()
    
    if (responseRequest.error == true) {
        return window.location = `${baseUrl}/search_onts_via_ssh?tab_id=${tabId}`
    }

    return window.location = `${baseUrl}/render_onts_table?tab_id=${tabId}`
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
    loadingAnimation(true)
    const baseUrl = "http://10.0.30.157:8000/generator"
    const idDevicesSelected = getIdDevicesSelected()

    if (idDevicesSelected.length == 0) {
        loadingAnimation(false)
        return alert('Selecione ao menos um dispositivo')
    }

    const maintenanceInfo = getMaintenanceInfoFromForm()

    if (maintenanceInfo.error) {
        loadingAnimation(false)
        return alert(maintenanceInfo.message)
    }

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'tabId': maintenanceInfo.tabId,
            'destinationGpon': maintenanceInfo.destinationGpon,
            'fileName': maintenanceInfo.fileName,
            'idDevicesSelected': maintenanceInfo.idDevicesSelected,
            'mode': 'generator'
        })
    }

    let getCommands = await fetch(`${baseUrl}/get_commands`, requestOptions)
    getCommands = await getCommands.json()
    
    if (getCommands.error) {
        messageError =  getCommands.message
        return window.location = `${baseUrl}/render_error_page?message=${messageError}`
    }
    return window.location = `${baseUrl}/render_page_commands?tab_id=${maintenanceInfo.tabId}`
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

async function searchOntsViaSsh(operationMode) {
    loadingAnimation(true)
    const baseUrl = "http://10.0.30.157:8000" + (operationMode == 'generator' ? '/generator' : '/attenuator')
    const loadingText = document.getElementById('loader-message')
    const pon = document.getElementById('pon').textContent
    const host = document.getElementById('host').textContent
    const socket = new WebSocket('ws://10.0.30.157:5678/get-onts')
    const tabId = getIdentificator()
    const onts = []
    let total_number_onts = 0
    let controllerPercentage = 0

    socket.onopen = () => {
        socket.send(JSON.stringify({
            pon, 
            host, 
            tab_id: tabId
        }))
        console.log('Sessão com o servidor Websocket iniciada')
    }

    socket.onmessage = (event) => {
        const currentMessage = JSON.parse(event.data)

        if (currentMessage.total_number_onts){
            total_number_onts = currentMessage.total_number_onts
            loadingText.textContent = `Carregando dados dos dispositivos - 0%`

        } else if (currentMessage.id) {
            controllerPercentage+=1
            let percentage = Math.trunc((100 * controllerPercentage) / total_number_onts)
            loadingText.textContent = `Carregando dados dos dispositivos  - ${percentage}%`
            onts.push(currentMessage)

        } else if (currentMessage.message == "No ont were found") {
            socket.close()
            alert('Não existem dispositivos na localização informada! Vamos te redirecionar para a homepage.')
            return window.location =  `${baseUrl}/home`
        }
    }

    socket.onclose = () => {
        console.log('Sessão com o servidor Websocket finalizada')
        return window.location = `${baseUrl}/render_onts_table?tab_id=${tabId}`
    }
}

async function saveInitialAttenuationState() {
    loadingAnimation(true)
    const baseUrl = "http://10.0.30.157:8000/attenuator"
    allDevicesSelected = checkIfAllDevicesIsSelected()

    if (!allDevicesSelected) {
        loadingAnimation(false)
        return alert('Você precisa selecionar todos os dispositivos')
    }

    const maintenanceInfo = getMaintenanceInfoFromForm()

    if (maintenanceInfo.error) {
        loadingAnimation(false)
        return alert(maintenanceInfo.message)
    }

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'tabId': maintenanceInfo.tabId,
            'destinationGpon': maintenanceInfo.destinationGpon,
            'fileName': maintenanceInfo.fileName,
            'unchangedDevices': maintenanceInfo.idDevicesSelected
        })
    }

    let saveAttenuationState = await fetch(`${baseUrl}/save_initial_attenuation_state`, requestOptions)
    saveAttenuationState = await saveAttenuationState.json()

    if (saveAttenuationState.error) {
        messageError = saveAttenuationState.message
        return window.location = `${baseUrl}/render_error_page?message=${messageError}`
    }

    return window.location = `${baseUrl}/render_attenuations_page?tab_id=${maintenanceInfo.tabId}`
}

function getMaintenanceInfoFromForm() {
    const destinationHost = document.getElementById('select-olt').value
    const destinationSlot = document.getElementById('select-slot').value
    const destinationPort = document.getElementById('select-port').value
    const fileName = document.getElementById('file-name').value
    const tabId = getIdentificator()

    if (!destinationHost || !destinationSlot || !destinationPort) {
        return { error: true, message: 'Preecha o F/S/P para prosseguir'}
    } else if (!fileName) {
        return { error: true, message: 'Digite um nome para o seu arquivo para prosseguir'}
    }

    const gponInfo = {
        destinationGpon: {
            'host': destinationHost,
            'gpon': `0/${destinationSlot}/${destinationPort}`
        },
        fileName,
        tabId,
        idDevicesSelected: getIdDevicesSelected()
    }

    return gponInfo
}

function checkIfAllDevicesIsSelected()  {
    const allDevices = document.querySelectorAll('#cbx-single-item')
    let allSelected = true

    for (let device of allDevices) {
            if (!device.checked) {
            allSelected = false
            break
        }
    }
    return allSelected
}

function getIdDevicesSelected() {
    const allDevices = document.querySelectorAll('#cbx-single-item')
    const idDevicesSelected = []

    allDevices.forEach((device) => {
        if (device.checked) {
            const deviceId = device.parentNode.parentNode.children[1].innerHTML
            idDevicesSelected.push(Number(deviceId))
        }
    })
    return idDevicesSelected
}

async function showAttenuation(attenuationId) {
    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'tabId': getIdentificator()
        })
    }

    let allAttenuations = await fetch('http://10.0.30.157:8000/attenuator/get_onts_to_render', requestOptions)
    allAttenuations = await allAttenuations.json()
    ontsInAttenuation = getOntsInAttenuation(attenuationId, allAttenuations)

    if(ontsInAttenuation.length == 0) return alert('Ocorreu um problema ao buscar as atenuações')

    renderAttenuationPage(ontsInAttenuation, attenuationId)
}

function getOntsInAttenuation(attenuationId, allAttenuations) {
    const onts = []
    const unchangedOnts = JSON.parse(allAttenuations.unchanged_onts.replaceAll("'", '"'))
    const attenuations = allAttenuations.attenuations

    if (attenuationId == 0) {
        return unchangedOnts
    }

    attenuations.forEach((attenuation) => {
        if (attenuationId == attenuation.attenuation_id) {

            unchangedOnts.forEach((ont) => {
                const allIdsInAttenuation = attenuation.onts
                const ontId = ont.id.toString()

                if (allIdsInAttenuation.includes(ontId)){
                    onts.push(ont)
                }
            })
        }
    })

    return onts
}

function renderAttenuationPage(ontsInAttenuation, attenuationId) {
    const table = document.getElementById('onts-table')
    const containerTable = document.getElementById('container-onts-table')
    const attenuationsTable =document.getElementById('attenuations-table')

    containerTable.style.display = 'block'
    attenuationsTable.style.display = 'none'

    ontsInAttenuation.forEach((ont) => {
        const tr = document.createElement('tr')
        const idElement = document.createElement('td')
        const snElement = document.createElement('td')
        idElement.textContent = ont.id
        snElement.textContent = ont.sn

        tr.append(idElement, snElement)
        table.append(tr)
    })

    const holdButton = document.createElement('button')
    holdButton.textContent = 'Manter'
    holdButton.setAttribute('onclick', 'maintainAttenuation()')
    containerTable.appendChild(holdButton)

    if (attenuationId != 0) {
        const discardButton = document.createElement('button')
        discardButton.textContent = 'Descartar'
        discardButton.setAttribute('onclick', `discardAttenuation(${attenuationId})`)
        containerTable.appendChild(discardButton)
    }
}

async function discardAttenuation(attenuationId) {
    loadingAnimation(true)

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'tabId': getIdentificator(),
            'attenuationId': attenuationId
        })
    }

    let discardSingleAttenuation = await fetch('http://10.0.30.157:8000/attenuator/discard_attenuation', requestOptions)
    discardSingleAttenuation = await discardSingleAttenuation.json()

    if (discardSingleAttenuation.error) {
        return alert('Ocorreu um erro ao remover a atenuação')
    }

    alert(`Atenuação ${attenuationId} removida com sucesso`)
    return window.location.reload()
}

function maintainAttenuation() {
    loadingAnimation(true)
    const tabId = getIdentificator()
    return window.location = `http://10.0.30.157:8000/attenuator/render_attenuations_page?tab_id=${tabId}`
}

function nextAttenuation() {
    loadingAnimation(true)
    const tabId = getIdentificator()
    return window.location = `http://10.0.30.157:8000/attenuator/next_attenuation?tab_id=${tabId}`
}

async function endAttenuation() {
    loadingAnimation(true)
    const tabId = getIdentificator()
    let endAttenuations = await fetch(`http://10.0.30.157:8000/attenuator/end_attenuations?tab_id=${tabId}`)
    endAttenuations = await endAttenuations.json()

    if (endAttenuations.error) {
        const messageError = endAttenuations.message
        return window.location = `http://10.0.30.157:8000/attenuator/render_error_page?message=${messageError}`
    }

    return window.location = `http://10.0.30.157:8000/attenuator/render_page_commands?tab_id=${tabId}`
}

