async function getReadyCommandFiles(){
    loadingAnimation(true)
    const selectedFilter = document.getElementById('filter-selected').value

    if (!selectedFilter) {
        loadingAnimation(false)
        return alert('Selecione um filtro')
    }

    loadingAnimation(false)
    window.location = `http://127.0.0.1:8000/files/get_files?filter=${selectedFilter}`
}

async function displayAllLogs(operationMode, registerId){
    const url = `http://127.0.0.1:8000/files/show_logs?tabId=${registerId}&operationMode=${operationMode}`
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