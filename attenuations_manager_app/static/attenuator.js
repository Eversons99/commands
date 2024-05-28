async function saveInitialAttenuationState() {
    loadingAnimation(true)
    const baseUrl = "http://commands.nmultifibra.com.br/attenuator"
    allDevicesSelected = checkIfAllDevicesIsSelected()

    if (!allDevicesSelected) {
        loadingAnimation(false)
        return alert('Você precisa selecionar todos os dispositivos')
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

    let allAttenuations = await fetch('http://commands.nmultifibra.com.br/attenuator/get_onts_to_render', requestOptions)
    allAttenuations = await allAttenuations.json()
    let ontsInAttenuation = getOntsInAttenuation(attenuationId, allAttenuations)

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
    const attenuationsTable = document.getElementById('attenuations-table')
    const divAttenuationBtn = document.getElementById('attenuations-btn')

    containerTable.style.display = 'flex'
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
    divAttenuationBtn.appendChild(holdButton)

    if (attenuationId != 0) {
        const discardButton = document.createElement('button')
        discardButton.textContent = 'Descartar'
        discardButton.setAttribute('onclick', `discardAttenuation(${attenuationId})`)
        divAttenuationBtn.appendChild(discardButton)
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

    let discardSingleAttenuation = await fetch('http://commands.nmultifibra.com.br/attenuator/discard_attenuation', requestOptions)
    discardSingleAttenuation = await discardSingleAttenuation.json()

    if (discardSingleAttenuation.error) {
        return alert('Ocorreu um erro ao remover a atenuação')
    }

    alert(`Atenuação ${attenuationId} removida com sucesso`)
    //return window.location.reload()
    return window.location = `http://commands.nmultifibra.com.br/attenuator/render_attenuations_page?tab_id=${getIdentificator()}`
}

function maintainAttenuation() {
    loadingAnimation(true)
    const tabId = getIdentificator()
    return window.location = `http://commands.nmultifibra.com.br/attenuator/render_attenuations_page?tab_id=${tabId}`
}

function nextAttenuation() {
    loadingAnimation(true)
    const tabId = getIdentificator()
    return window.location = `http://commands.nmultifibra.com.br/attenuator/next_attenuation?tab_id=${tabId}`
}

async function endAttenuation() {
    const confirmEndAttenuation = confirm('Realmente deseja finalizar as atenuações?')
    
    if(!confirmEndAttenuation) return 

    loadingAnimation(true)

    const attenuationsTable = document.getElementById('attenuations-table')
    const attenuations = attenuationsTable.childNodes[1].childNodes

    if (attenuations.length == 2) {
        loadingAnimation(false)
        return alert('Nenhuma atenuação coletada, impossível prosseguir')
    }

    const tabId = getIdentificator()
    let endAttenuations = await fetch(`http://commands.nmultifibra.com.br/attenuator/end_attenuations?tab_id=${tabId}`)
    endAttenuations = await endAttenuations.json()

    if (endAttenuations.error) {
        const messageError = endAttenuations.message
        return window.location = `http://commands.nmultifibra.com.br/attenuator/render_error_page?message=${messageError}`
    }
    return window.location = `http://commands.nmultifibra.com.br/attenuator/render_page_commands?tab_id=${tabId}`
}
