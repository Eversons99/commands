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

async function displayLogs(){

}

