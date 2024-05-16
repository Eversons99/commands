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
    
    if (operationMode == 'attenuator' && responseRequest.error == true) {
        let messageError = responseRequest.message

        if (messageError == 'No onts were found') {
            messageError = 'Nenhuma ONU na porta informada'
        }

        return window.location = `${baseUrl}/render_error_page?message=${messageError}`
    }
    else if (responseRequest.error == true) {
        return window.location = `${baseUrl}/search_onts_via_ssh?tab_id=${tabId}`
    }

    return window.location = `${baseUrl}/render_onts_table?tab_id=${tabId}`
}

function getIdentificator() {
    const identificatorTab = window.sessionStorage.getItem('tabId')
    return identificatorTab
}

async function generateCommands() {
    loadingAnimation(true)
    const baseUrl = "http://10.0.30.157:8000/generator"
    const idDevicesSelected = getIdDevicesSelected()

    if (idDevicesSelected.length == 0) {
        loadingAnimation(false)
        return alert('Selecione ao menos um dispositivo')
    }

    const maintenanceInfo = await getMaintenanceInfoFromForm()

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

async function getMaintenanceInfoFromForm() {
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
    
    const checkFileName = await checkFileNameExists(fileName)
    if (checkFileName.used) {
        return  { error: true, message: `O nome ${fileName} já está em uso, escolha outro` }
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

async function checkFileNameExists(fileName){
    let allFileNames = await fetch(`http://10.0.30.157:8000/shared-core/check_file_names?fileName=${fileName}`)
    allFileNames = await allFileNames.json()

    return allFileNames
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

async function apllyCommands(operationMode, rollback) {
    const confirmApply = confirm(rollback ? 'Confirm a aplicação dos comandos de rollack?' : 'Confirme a aplicação dos comandos')

    if (!confirmApply) return

    loadingAnimation(true)
    const maintenanceInfo = await getMaintenanceInfo(operationMode)
    const socket = new WebSocket('ws://10.0.30.157:8001/apply-commands')
    const loadingText = document.getElementById('loader-message')
    const commandsApplied = []
    let operationStatus
    let connectionWithErr
    rollback = rollback ? true : false
    maintenanceInfo.rollback = rollback ? true : false

    socket.onerror = () => {
        loadingAnimation(false)
        connectionWithErr = true
        alert('Ocorreu um erro ao conectar ao servidor WebSocket.');
    }

    socket.onopen = () => {
        socket.send(JSON.stringify({
            maintenanceInfo
        }))
        console.log('Sessão com o servidor Websocket iniciada')
    }

    socket.onmessage = (event) => {
        const currentMessage = JSON.parse(event.data)
        if (currentMessage.command) {
            let commandLog = currentMessage.command
            loadingText.textContent = `Aplicando comando: ${commandLog}`
            commandsApplied.push(currentMessage)
        }
    }

    socket.onclose = async () => {
        if (!connectionWithErr){
            loadingAnimation(false)
            await updateStatusAppliedCommands(operationMode, maintenanceInfo, rollback)
            await showLogs(commandsApplied, operationMode, rollback)
            console.log('Sessão com o servidor Websocket finalizada')
            return operationStatus
        }
    }
}

async function getMaintenanceInfo(operationMode) {
    const url = `http://10.0.30.157:8000/${operationMode}/get_maintenance_info`
    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'tabId': getIdentificator()
        })
    }
     
    let maintenanceInfo = await fetch(url, requestOptions)
    maintenanceInfo = await maintenanceInfo.json()

    return maintenanceInfo
}

async function showLogs(logs, operationMode, rollback) {
    const tabId = getIdentificator()
    const baseUrl = `http://10.0.30.157:8000/${operationMode}`
    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'rollback': rollback,
            'tabId': tabId,
            'logs': logs
        })
    }
    
    let saveCommands = await fetch(`${baseUrl}/save_logs`, requestOptions)
    saveCommands = await saveCommands.json()

    if (saveCommands.error) return alert(saveCommands.message)

    return window.location = `${baseUrl}/render_logs?tab_id=${tabId}&rollback=${rollback}` 
}

async function downloadCommandsFile(operationMode) {
    const tab_id = getIdentificator()
    const url = `http://10.0.30.157:8000/${operationMode}/download_command_file?tab_id=${tab_id}`
    const div = document.querySelector('.action-buttuns')
    const link = document.createElement('a')

    link.setAttribute('href', url)
    link.setAttribute('id', 'link-download')
    div.appendChild(link)

    const elementLink = document.getElementById('link-download')
    elementLink.click()
}

async function discardCommands(operationMode) {
    const confirmDelete = confirm('Realmente deseja deletar os comandos? TODOS os dados serão perdidas?')

    if (!confirmDelete) return

    const donwloadButton = document.getElementById('btn-save')
    const url = `http://10.0.30.157:8000/${operationMode}/discard_commands`
    const requestOptions = {
        method: 'DELETE',
        headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'tabId': getIdentificator()
        })
    }

    let removeCommands = await fetch(url, requestOptions)
    removeCommands = await removeCommands.json()
    donwloadButton.disabled = true

    if (!removeCommands.error) {
        const removeButton = document.getElementById('btn-discard')
        removeButton.disabled = true
    }
    alert(removeCommands.message)
    return window.location = 'http://10.0.30.157:8000/'
}

async function updateStatusAppliedCommands(operationMode, maintenanceInfo, rollback){
    const queryParams = `tabId=${maintenanceInfo.register_id}&rollback=${rollback}`
    const url = `http://10.0.30.157:8000/${operationMode}/update_status_applied_commands?${queryParams}`
    let updateInfo = await fetch(url)
    updateInfo = await updateInfo.json()

    if (updateInfo.error) {
        return alert(updateInfo.message)
    }
}