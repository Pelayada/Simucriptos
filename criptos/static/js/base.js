const btnFrom = document.getElementById("buttonFrom");
const btnCancel = document.getElementById("cancel");
const xhr = new XMLHttpRequest();
const inputFrom = document.getElementById("QFrom");

function reqHandler() {
    if (this.readyState === 4 && this.status == 200) { 
        const valueFrom = document.getElementById("QFrom").value;
        const selectTo = document.getElementById("selectTo").value;
        const valueTo = document.getElementById("QTo");
        const valueQPU = document.getElementById("QPU");

        let respuesta = JSON.parse(this.responseText)
        valueTo.value = (respuesta['data']['quote'][selectTo]['price']).toFixed(3);
        valueQPU.value = (valueFrom/valueTo.value).toFixed(3);
    }
}

function btnClickFrom() {
    const selectFrom = document.getElementById("selectFrom").value;
    const valueFrom = document.getElementById("QFrom").value;
    const selectTo = document.getElementById("selectTo").value;
    
    if(isNaN(valueFrom)){
        addError();
    } else {
        xhr.open('GET', `/coin?amount=${valueFrom}&symbol=${selectFrom}&convert=${selectTo}`)
        xhr.send();
    }   
}

function btnClickCancel() {
    document.getElementById("QFrom").value = "";
    document.getElementById("QTo").value = "";
    document.getElementById("QPU").value = "";
}

function resetError() {
    var errorQFrom = document.getElementsByClassName("field-error")
    if (errorQFrom.length > 0) {
        for (i = 0; i < errorQFrom.length; i++){
            errorQFrom[i].parentNode.removeChild(errorQFrom[i])
        }   
    };
}

function addError () {
    var errorQFrom = document.getElementsByClassName("field-error")
    if (errorQFrom.length === 0){
        var newDiv = document.createElement("p"); 
        newDiv.setAttribute('class', 'field-error');
        var newContent = document.createTextNode("Tiene que ser un número valido."); 
        newDiv.appendChild(newContent);
  
        var currentDiv = document.getElementById("divQ"); 
        currentDiv.insertBefore(newDiv, currentDiv.lastChild); 
    }
     
}

xhr.onload = reqHandler
btnFrom.addEventListener('click', btnClickFrom)
btnCancel.addEventListener('click', btnClickCancel)
inputFrom.addEventListener('focus', resetError)
