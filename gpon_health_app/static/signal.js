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

// Oculta a div principal e mostra a div com o modo de consulta selecionado
async function showQueryMode() { 
    const queryMode = document.getElementById('select-query-mode').value
    const queryModeDiv = document.getElementById('query-mode-div')

    if (!queryMode) return alert("Selectione o modo de consulta")

    queryModeDiv.style.display = "none"

    if (queryMode == 'ID do cliente') {
        const clientIdDiv = document.getElementById('client-id')
        clientIdDiv.style.display = 'flex'

    } else if (queryMode == 'Localização PON') {
        const ponDiv = document.getElementById('pon')
        ponDiv.style.display = 'flex'
    }
}

/* 
Verifica qual o modo de consulta selecionado e faz a chamada para a função que faz a 
consulta de sinal
*/
async function makeSignalQuery(queryMode){
    if (queryMode == 'ID do cliente') {
        const validClientId = validInputClientId()
        if (validClientId.error) return alert(validClientId.message)

        const requestInfo = {
            queryMode:'via_id',
            queryValue: validClientId.idClient
        }
        getSignalAverage(requestInfo)

    } else if (queryMode == 'Localização PON') {
        const validPon = validInputPon()
        if (validPon.error) return alert(validPon.message)

        const requestInfo = {
            queryMode: 'via_pon',
            queryValue: JSON.stringify(validPon.gpon)
        }
        getSignalAverage(requestInfo)
    }
}


// Valida a entrada do usuário
function validInputClientId() {
    const clientIdInput = document.getElementById('client-id-input').value
    if (!clientIdInput) return { error: true, message: 'Preencha o código do cliente' }

    return { idClient: clientIdInput }
}

// Valida a entrada do usuário
function validInputPon() {
    const olt = document.getElementById('select-olt').value
    const slot = document.getElementById('select-slot').value
    const port = document.getElementById('select-port').value
    
    if (!slot || !port) {
        return { error: true, message: "ATENÇÃO: Preencha o F/S/P!" } 
    } else if (!olt) {
        return { error: true, message: "Escolha uma OLT para prosseguir" } 
    }

    const locationPon = {
        gpon: {
            olt: olt,
            pon: `0/${slot}/${port}`
        }

    }
    return locationPon
}

// Faz a requisição para o backend retornar as informações da consulta
async function getSignalAverage(requestInfo) {
    loadingAnimation(true)
    const queryMode = requestInfo.queryMode
    const queryValue = requestInfo.queryValue

    window.location = `http://168.0.96.11:50066/optical/get-signal-information?queryMode=${queryMode}&queryValue=${queryValue}`
}

/* 
Valida o input do usuário e Faz a requisição para o backend retornar as informações 
da consulta, função usada quando cliente tem mais de um cadasatro
*/
function makeSignalQueryByTable() {
    loadingAnimation(true)
    let allPons =  document.getElementsByClassName('pon-table-row')
    let amountOfItemsSelected = 0
    let selectedOlt
    let selectedPon
    
    for (pon of allPons) {
        const inputCheckboxSelected = pon.childNodes[1].childNodes[0].checked
        
        if (inputCheckboxSelected) {
            selectedOlt = pon.childNodes[3].textContent
            selectedPon = pon.childNodes[5].textContent
            amountOfItemsSelected += 1
        }
    }

    if (amountOfItemsSelected > 1) {
        loadingAnimation(false)
        return alert('Selecione apenas um para prosseguir')
    }    
    if (!selectedOlt || !selectedPon) {
        loadingAnimation(false)
        return alert('Selecione um registro para prosseguir')

    }
    const requestInfo = {
        queryMode: 'via_pon',
        queryValue: JSON.stringify({
            olt: selectedOlt,
            pon: selectedPon
        })
    }

    getSignalAverage(requestInfo)
}

function updateDescription() {
    loadingAnimation(true)

    const olt = document.getElementById('select-olt').value
    const gpon = `0/${document.getElementById('select-slot').value}/${document.getElementById('select-port').value}`
    let primary = document.getElementById('select-primary').value
    let cable = document.getElementById('select-cable').value

    if (!document.getElementById('select-slot').value || !document.getElementById('select-port').value ) {
        loadingAnimation(false)
        return window.alert('Preecha o F/S/P para prosseguir')
    } else if (!olt) {
        loadingAnimation(false)
        return window.alert('Selecione a OLT para prosseguir')
    } else if (!primary) {
        loadingAnimation(false)
        return window.alert('Selecione a PRIMÁRIA para prosseguir')
    } else if (!cable) {
        loadingAnimation(false)
        return window.alert('Selecione o CABO para prosseguir')
    }

    if(primary < 1 || primary > 72) {
        loadingAnimation(false)
        return window.alert('Número da primária inválido, por favor, insira um número entre 1 e 72!')
    } else if (primary < 10) {
        primary = `0${primary}`
    }


    if(cable < 1 || cable > 13) {
        return window.alert('Número do cabo inválido, por favor, insira um número entre 1 e 13!')
    } else if (cable < 10) {
        cable = `0${cable}`
    }

    window.location = `http://168.0.96.11:50066/optical/update-primary-description?olt=${olt}&gpon=${gpon}&primary=${primary}&cable=${cable}`
}