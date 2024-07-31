async function getReadyCommandFiles(){
    loadingAnimation(true)
    const selectedFilter = document.getElementById('filter-selected').value

    if (!selectedFilter) {
        loadingAnimation(false)
        return alert('Selecione um filtro')
    }

    loadingAnimation(false)
    window.location = `http://dk.commands.nmultifibra.com.br/maintenance/files/get_files?filter=${selectedFilter}`
}

async function displayAllLogs(operationMode, registerId){
    const lastFilter = window.location.href
    const url = `http://dk.commands.nmultifibra.com.br/maintenance/files/show_logs?tabId=${registerId}&operationMode=${operationMode}&lastFilter=${lastFilter}`
    return window.location = url
}


function resultsTabsButton(e) {
    const logsDiv = document.getElementById('logs')
    const rollbackLogsDiv = document.getElementById('rollback-logs')

    const logsButton = document.getElementById('logs-btn')
    const rollbackLogsButton = document.getElementById('rollback-logs-btn')

    if (e.target.id == 'logs-btn') {
        logsDiv.setAttribute('class', 'active-result')
        rollbackLogsDiv.setAttribute('class', 'inactive-result')
        
        logsButton.setAttribute('class', 'active-btn')
        rollbackLogsButton.setAttribute('class', 'inactive-btn')
    }
    if (e.target.id == 'rollback-logs-btn') {
        rollbackLogsDiv.setAttribute('class', 'active-result')
        logsDiv.setAttribute('class', 'inactive-result')

        rollbackLogsButton.setAttribute('class', 'active-btn')
        logsButton.setAttribute('class', 'inactive-btn')
    }
}

function showOperationList(){
    const operationList = document.querySelector('.operation-list')
    
    if (!operationList.style.display || operationList.style.display == 'none') {
        operationList.style.display = 'block'
    } else {
        operationList.style.display = 'none'
    }
}

function handleActionChange(selectElement) {
    let selectedValue = selectElement.value;
    let moduleName = selectElement.parentNode.parentNode.childNodes[7].textContent.toLowerCase()
    let registerId = selectElement.parentNode.parentNode.childNodes[1].textContent.toLowerCase()
    
    switch (selectedValue) {
        case "apply":
            apllyCommands(moduleName, false, registerId);
            break;
        case "discard":
            discardCommands(moduleName, registerId);
            break;
        case "download":
            downloadCommandsFile(moduleName, registerId);
            break;
        case "logs":
            displayAllLogs(moduleName, registerId);
            break;
        default:
            break;
    }
    selectElement.value = "...";
}