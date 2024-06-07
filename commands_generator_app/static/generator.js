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

async function searchOntsViaSsh() {
    loadingAnimation(true)
    const baseUrl = 'http://localhost:8000/maintenance'
    const loadingText = document.getElementById('loader-message')
    const pon = document.getElementById('pon').textContent
    const host = document.getElementById('host').textContent
    const socket = new WebSocket('ws://127.0.0.1:5678/get-onts')
    const tabId = getIdentificator()
    const onts = []
    let sessionStarted = false
    let totalNumberOnts = 0
    let controllerPercentage = 0

    try {
        socket.onopen = () => {
            socket.send(JSON.stringify({
                pon, 
                host, 
                tab_id: tabId
            }))
            sessionStarted = true
            loadingText.textContent = 'Iniciando sessão com o servidor websocket...'
            console.log('Sessão com o servidor Websocket iniciada')
        }
    
        socket.onmessage = (event) => {
            const currentMessage = JSON.parse(event.data)

            if (currentMessage.total_number_onts) {
                totalNumberOnts = currentMessage.total_number_onts
                loadingText.textContent = `Carregando dados dos dispositivos - 0%`

            } else if (currentMessage.id) {
                controllerPercentage+=1
                let percentage = Math.trunc((100 * controllerPercentage) / totalNumberOnts)
                loadingText.textContent = `Carregando dados dos dispositivos  - ${percentage}%`
                onts.push(currentMessage)

            } else if (currentMessage.message == "No ont were found") {
                socket.close()
                alert('Não existem dispositivos na localização informada! Vamos te redirecionar para a homepage.')
                return window.location = `${baseUrl}/generator/home`
            }
        }
    
        socket.onclose = () => {
            console.log('Sessão com o servidor Websocket finalizada')

            if (!sessionStarted) {
                alert('Ocorreu um erro ao se conectar ao servidor websocket')
                return window.location = `${baseUrl}/generator/home`

            } else if (!totalNumberOnts) {
                alert('Nenhum dispositivo foi encontrado na localização informada!')
                return window.location = `${baseUrl}/generator/home`
            }
            return window.location = `${baseUrl}/shared_core/render_onts_table?tab_id=${tabId}&mode=generator`
        }

        socket.onerror = (event) => {
            loadingAnimation(false)
            alert(`Ocorreu um erro durante a conexão websocket. Err: ${event.message}`);
        }
    } catch (error) {
        return alert(error)
    }
}

async function generateCommands() {
    loadingAnimation(true)
    const baseUrl = "http://localhost:8000/maintenance"
    const idDevicesSelected = getIdDevicesSelected()
    const loadingText = document.getElementById('loader-message')
    loadingText.textContent = 'Gerando comandos...'

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

    try {
        let getCommands = await fetch(`${baseUrl}/shared_core/generate_commands`, requestOptions)
        getCommands = await getCommands.json()
        
        if (getCommands.error) {
            const messageError = getCommands.message
            return window.location = `${baseUrl}/render_error_page?message=${messageError}`
        }
        return window.location = `${baseUrl}/shared_core/render_page_commands?tab_id=${maintenanceInfo.tabId}&mode=generator`
    } catch (error) {
        loadingAnimation(false)
        return alert(`Ocorreu um erro ao gerar os comandos. Err:${error}`)
    } 
}
