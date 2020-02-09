const btnFrom = document.getElementById("buttonFrom");
const xhr = new XMLHttpRequest();

function reqHandler() {
    if (this.readyState === 4 && this.status == 200) { 
        const valueFrom = document.getElementById("QFrom").value;
        const selectTo = document.getElementById("selectTo").value;
        const valueTo = document.getElementById("QTo")
        const valueQPU = document.getElementById("QPU")

        let respuesta = JSON.parse(this.responseText)
        valueTo.value = (respuesta['data']['quote'][selectTo]['price']).toFixed(3);
        valueQPU.value = (valueFrom/valueTo.value).toFixed(3)
    }
}

function btnClickFrom(ev) {
    const selectFrom = document.getElementById("selectFrom").value;
    const valueFrom = document.getElementById("QFrom").value;
    const selectTo = document.getElementById("selectTo").value;


    xhr.open('GET', `/coin?amount=${valueFrom}&symbol=${selectFrom}&convert=${selectTo}`)
    xhr.send();
}

xhr.onload = reqHandler
btnFrom.addEventListener('click', btnClickFrom)